import base64
import json
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.vehicle import Vehicle
from app.services.tesla_client import encrypt_token, get_vehicles_list

router = APIRouter(prefix="/api/auth", tags=["auth"])


class ConnectRequest(BaseModel):
    access_token: str
    refresh_token: str

    @field_validator("access_token", "refresh_token", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")


def _parse_token_expiry(access_token: str) -> datetime:
    """Extract expiry from JWT payload. Falls back to 8 hours from now."""
    try:
        payload = access_token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        claims = json.loads(base64.b64decode(payload))
        return (datetime.fromtimestamp(claims["exp"], tz=timezone.utc) - timedelta(seconds=300)).replace(tzinfo=None)
    except Exception:
        return datetime.utcnow() + timedelta(hours=8)


class ValidateTokenRequest(BaseModel):
    access_token: str

    @field_validator("access_token", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")


@router.post("/validate-token")
async def validate_token(body: ValidateTokenRequest):
    """Test an access token against Tesla API without storing anything."""
    token = body.access_token

    # Decode JWT claims for expiry and region info
    token_info: dict = {}
    try:
        payload = token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        claims = json.loads(base64.b64decode(payload))
        exp_dt = datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
        aud = claims.get("aud", [])
        if isinstance(aud, str):
            aud = [aud]
        region = next(
            (e for e in aud if "fleet-api.prd" in e),
            "fleet-api.prd.na.vn.cloud.tesla.com (default)",
        )
        token_info = {
            "expires_at": exp_dt.strftime("%Y-%m-%d %H:%M UTC"),
            "expired": exp_dt < datetime.now(tz=timezone.utc),
            "region": region,
        }
    except Exception:
        token_info = {"expires_at": None, "expired": None, "region": "unknown"}

    try:
        from app.services.tesla_client import get_vehicles_list
        vehicles = await get_vehicles_list(token)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        return {
            "valid": False,
            "error": f"Tesla API returned HTTP {status} — token is invalid or expired.",
            **token_info,
            "vehicle_count": 0,
            "vehicles": [],
        }
    except Exception as exc:
        return {
            "valid": False,
            "error": f"Could not reach Tesla API: {exc}",
            **token_info,
            "vehicle_count": 0,
            "vehicles": [],
        }

    return {
        "valid": True,
        "error": None,
        **token_info,
        "vehicle_count": len(vehicles),
        "vehicles": [v.get("display_name") or v.get("vin") for v in vehicles],
    }


@router.post("/connect")
async def connect(body: ConnectRequest, db: AsyncSession = Depends(get_db)):
    """Store Tesla tokens pasted from myteslamate.com or tesla_auth."""
    try:
        vehicles = await get_vehicles_list(body.access_token)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status in (401, 403):
            detail = (
                f"Tesla API rejected the token (HTTP {status}). "
                "The access token is invalid or expired — get a fresh token from "
                "myteslamate.com and paste it again."
            )
        else:
            detail = f"Tesla API returned HTTP {status}. Response: {exc.response.text[:200]}"
        raise HTTPException(status_code=400, detail=detail)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not reach Tesla API: {exc}",
        )

    if not vehicles:
        raise HTTPException(status_code=400, detail="No vehicles found for this account.")

    expires_at = _parse_token_expiry(body.access_token)

    for v in vehicles:
        vin = v.get("vin")
        if not vin:
            continue
        result = await db.execute(select(Vehicle).where(Vehicle.vin == vin))
        vehicle = result.scalar_one_or_none()
        if vehicle is None:
            vehicle = Vehicle(vin=vin)
            db.add(vehicle)

        vehicle.display_name = v.get("display_name") or v.get("vehicle_name")
        vehicle.model = "Model 3"
        vehicle.access_token = encrypt_token(body.access_token)
        vehicle.refresh_token = encrypt_token(body.refresh_token)
        vehicle.token_expires_at = expires_at
        vehicle.is_active = True

    await db.commit()
    return {"message": "Connected", "vehicle_count": len(vehicles)}


@router.get("/status")
async def status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle).where(Vehicle.is_active == True))
    vehicles = result.scalars().all()
    return {
        "authenticated": len(vehicles) > 0,
        "vehicle_count": len(vehicles),
    }


@router.delete("/logout")
async def logout(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle))
    vehicles = result.scalars().all()
    for v in vehicles:
        v.is_active = False
        v.access_token = None
        v.refresh_token = None
    await db.commit()
    return {"message": "Logged out"}
