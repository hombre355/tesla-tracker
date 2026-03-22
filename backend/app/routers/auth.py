import base64
import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.vehicle import Vehicle
from app.services.tesla_client import encrypt_token, get_vehicles_list

router = APIRouter(prefix="/api/auth", tags=["auth"])


class ConnectRequest(BaseModel):
    access_token: str
    refresh_token: str


def _parse_token_expiry(access_token: str) -> datetime:
    """Extract expiry from JWT payload. Falls back to 8 hours from now."""
    try:
        payload = access_token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        claims = json.loads(base64.b64decode(payload))
        return datetime.fromtimestamp(claims["exp"], tz=timezone.utc) - timedelta(seconds=300)
    except Exception:
        return datetime.now(timezone.utc) + timedelta(hours=8)


@router.post("/connect")
async def connect(body: ConnectRequest, db: AsyncSession = Depends(get_db)):
    """Store Tesla tokens pasted from myteslamate.com or tesla_auth."""
    try:
        vehicles = await get_vehicles_list(body.access_token)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not reach Tesla API — check that the access token is valid and not expired.",
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
