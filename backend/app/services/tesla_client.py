import base64
import json
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.vehicle import Vehicle


def get_fernet() -> Optional[Fernet]:
    if not settings.encryption_key:
        return None
    return Fernet(settings.encryption_key.encode())


def encrypt_token(token: str) -> str:
    f = get_fernet()
    if f is None:
        return token
    return f.encrypt(token.encode()).decode()


def decrypt_token(token: str) -> str:
    f = get_fernet()
    if f is None:
        return token
    return f.decrypt(token.encode()).decode()


OWNER_API_BASE = "https://owner-api.teslamotors.com"
FLEET_BASE = "https://fleet-api.prd.na.vn.cloud.tesla.com"
TOKEN_URL = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token"

# Owner API expects requests to look like they come from the Tesla mobile app
TESLA_HEADERS = {
    "User-Agent": "Tesla/4.30.6 (iPhone; iOS 17.4; Scale/3.00)",
    "X-Tesla-User-Agent": "TeslaApp/4.30.6",
}


def api_base_from_token(access_token: str) -> str:
    """Return the correct API base URL for this token.

    Tokens from registered Fleet API apps carry a 'fleet-api.prd' audience
    claim — use the regional Fleet API endpoint for those.  Tokens from
    tesla_auth / TeslaMate (basic scopes only) have no such claim, so fall
    back to the older Owner API which accepts them.
    """
    try:
        payload = access_token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        claims = json.loads(base64.b64decode(payload))
        aud = claims.get("aud", [])
        if isinstance(aud, str):
            aud = [aud]
        for entry in aud:
            if "fleet-api.prd" in entry:
                return entry.rstrip("/")
    except Exception:
        pass
    return OWNER_API_BASE


async def refresh_access_token(vehicle: Vehicle, db: AsyncSession) -> str:
    """Refresh the access token using the stored refresh token. Returns new access token."""
    refresh_token = decrypt_token(vehicle.refresh_token)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    vehicle.access_token = encrypt_token(data["access_token"])
    vehicle.refresh_token = encrypt_token(data["refresh_token"])
    expires_in = data.get("expires_in", 3600)
    from datetime import timedelta
    vehicle.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 300)
    await db.commit()
    return data["access_token"]


async def get_access_token(vehicle: Vehicle, db: AsyncSession) -> str:
    """Return a valid access token, refreshing if needed."""
    if vehicle.token_expires_at and vehicle.token_expires_at < datetime.utcnow():
        return await refresh_access_token(vehicle, db)
    return decrypt_token(vehicle.access_token)


async def get_vehicle_data(vehicle: Vehicle, db: AsyncSession) -> Optional[dict[str, Any]]:
    """Fetch live vehicle_data from Tesla Fleet API."""
    token = await get_access_token(vehicle, db)
    base = api_base_from_token(token)
    url = f"{base}/api/1/vehicles/{vehicle.vin}/vehicle_data"
    params = {"endpoints": "charge_state,drive_state,vehicle_state,climate_state"}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers={**TESLA_HEADERS, "Authorization": f"Bearer {token}"}, params=params)
        if resp.status_code == 408:
            return None  # vehicle asleep
        resp.raise_for_status()
        return resp.json().get("response", {})


async def get_charging_history(
    vehicle: Vehicle, db: AsyncSession, page: int = 1
) -> list[dict[str, Any]]:
    """Fetch charging session history from Tesla Fleet API."""
    token = await get_access_token(vehicle, db)
    base = api_base_from_token(token)
    url = f"{base}/api/1/dx/charging/history"
    params = {"vin": vehicle.vin, "pageNo": page, "pageSize": 50}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers={**TESLA_HEADERS, "Authorization": f"Bearer {token}"}, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])


async def get_vehicles_list(access_token: str) -> list[dict[str, Any]]:
    """Fetch the list of vehicles associated with the account."""
    base = api_base_from_token(access_token)
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{base}/api/1/vehicles",
            headers={**TESLA_HEADERS, "Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json().get("response", [])
