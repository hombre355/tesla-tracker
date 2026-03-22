import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.vehicle import Vehicle
from app.services.tesla_client import encrypt_token, get_vehicles_list

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In-memory CSRF state store (fine for single-user personal app)
_csrf_states: dict[str, str] = {}

SCOPES = "openid offline_access vehicle_device_data vehicle_location vehicle_charging_cmds"


@router.get("/login")
async def login():
    state = secrets.token_urlsafe(32)
    _csrf_states[state] = state
    params = {
        "response_type": "code",
        "client_id": settings.tesla_client_id,
        "redirect_uri": settings.tesla_redirect_uri,
        "scope": SCOPES,
        "state": state,
        "audience": settings.tesla_audience,
    }
    url = f"{settings.tesla_auth_url}?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/callback")
async def callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    if state not in _csrf_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    del _csrf_states[state]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            settings.tesla_token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.tesla_client_id,
                "client_secret": settings.tesla_client_secret,
                "code": code,
                "redirect_uri": settings.tesla_redirect_uri,
                "audience": settings.tesla_audience,
            },
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {resp.text}")
        token_data = resp.json()

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    expires_in = token_data.get("expires_in", 3600)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 300)

    vehicles = await get_vehicles_list(access_token)
    for v in vehicles:
        vin = v.get("vin")
        if not vin:
            continue
        existing = await db.execute(select(Vehicle).where(Vehicle.vin == vin))
        vehicle = existing.scalar_one_or_none()
        if vehicle is None:
            vehicle = Vehicle(vin=vin)
            db.add(vehicle)

        vehicle.display_name = v.get("display_name") or v.get("vehicle_name")
        vehicle.model = "Model 3"
        vehicle.access_token = encrypt_token(access_token)
        vehicle.refresh_token = encrypt_token(refresh_token)
        vehicle.token_expires_at = expires_at
        vehicle.is_active = True

    await db.commit()
    return RedirectResponse(f"{settings.frontend_url}/dashboard")


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
