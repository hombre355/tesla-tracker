"""Tests for POST /api/auth/connect, GET /api/auth/status, DELETE /api/auth/logout."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle import Vehicle
from app.services.tesla_client import encrypt_token

VEHICLES_URL = "https://owner-api.teslamotors.com/api/1/vehicles"

FAKE_ACCESS = "fake.access.token"
FAKE_REFRESH = "fake.refresh.token"

VEHICLE_RESPONSE = {
    "response": [{"vin": "5YJ3E1EAXKF000001", "display_name": "Test Tesla"}]
}


class TestConnect:
    async def test_nominal(self, client: AsyncClient, httpx_mock, db_session: AsyncSession):
        """Valid tokens + Tesla returns a vehicle → 200, vehicle stored in DB."""
        httpx_mock.add_response(method="GET", url=VEHICLES_URL, json=VEHICLE_RESPONSE)

        resp = await client.post(
            "/api/auth/connect",
            json={"access_token": FAKE_ACCESS, "refresh_token": FAKE_REFRESH},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["vehicle_count"] == 1

        result = await db_session.execute(select(Vehicle))
        vehicles = result.scalars().all()
        assert len(vehicles) == 1
        assert vehicles[0].vin == "5YJ3E1EAXKF000001"
        assert vehicles[0].is_active is True

    async def test_tesla_api_error(self, client: AsyncClient, httpx_mock):
        """Tesla API returns 401 → 400 with descriptive message."""
        httpx_mock.add_response(method="GET", url=VEHICLES_URL, status_code=401)

        resp = await client.post(
            "/api/auth/connect",
            json={"access_token": FAKE_ACCESS, "refresh_token": FAKE_REFRESH},
        )

        assert resp.status_code == 400
        assert "401" in resp.json()["detail"]

    async def test_no_vehicles(self, client: AsyncClient, httpx_mock):
        """Tesla API returns empty vehicle list → 400."""
        httpx_mock.add_response(
            method="GET", url=VEHICLES_URL, json={"response": []}
        )

        resp = await client.post(
            "/api/auth/connect",
            json={"access_token": FAKE_ACCESS, "refresh_token": FAKE_REFRESH},
        )

        assert resp.status_code == 400
        assert "No vehicles found" in resp.json()["detail"]

    async def test_missing_access_token(self, client: AsyncClient):
        """Missing required field → 422."""
        resp = await client.post(
            "/api/auth/connect", json={"refresh_token": FAKE_REFRESH}
        )
        assert resp.status_code == 422

    async def test_missing_refresh_token(self, client: AsyncClient):
        """Missing required field → 422."""
        resp = await client.post(
            "/api/auth/connect", json={"access_token": FAKE_ACCESS}
        )
        assert resp.status_code == 422

    async def test_empty_body(self, client: AsyncClient):
        """No body at all → 422."""
        resp = await client.post("/api/auth/connect", json={})
        assert resp.status_code == 422

    async def test_token_with_embedded_newlines(
        self, client: AsyncClient, httpx_mock, db_session: AsyncSession
    ):
        """Tokens with embedded newlines (common paste artifact) should be stripped and accepted."""
        httpx_mock.add_response(method="GET", url=VEHICLES_URL, json=VEHICLE_RESPONSE)

        resp = await client.post(
            "/api/auth/connect",
            json={
                "access_token": f"fake\n.access\n.token",
                "refresh_token": f"fake\n.refresh\n.token",
            },
        )

        assert resp.status_code == 200

    async def test_token_with_surrounding_whitespace(
        self, client: AsyncClient, httpx_mock, db_session: AsyncSession
    ):
        """Tokens with leading/trailing spaces should be stripped and accepted."""
        httpx_mock.add_response(method="GET", url=VEHICLES_URL, json=VEHICLE_RESPONSE)

        resp = await client.post(
            "/api/auth/connect",
            json={
                "access_token": f"  {FAKE_ACCESS}  ",
                "refresh_token": f"\t{FAKE_REFRESH}\t",
            },
        )

        assert resp.status_code == 200

    async def test_reconnect_updates_existing_vehicle(
        self, client: AsyncClient, httpx_mock, db_session: AsyncSession
    ):
        """Connecting again with same VIN updates the existing row, doesn't create a duplicate."""
        httpx_mock.add_response(method="GET", url=VEHICLES_URL, json=VEHICLE_RESPONSE)
        await client.post(
            "/api/auth/connect",
            json={"access_token": FAKE_ACCESS, "refresh_token": FAKE_REFRESH},
        )

        httpx_mock.add_response(method="GET", url=VEHICLES_URL, json=VEHICLE_RESPONSE)
        resp = await client.post(
            "/api/auth/connect",
            json={"access_token": "new.access.token", "refresh_token": "new.refresh.token"},
        )

        assert resp.status_code == 200
        result = await db_session.execute(select(Vehicle))
        vehicles = result.scalars().all()
        assert len(vehicles) == 1


class TestStatus:
    async def test_unauthenticated(self, client: AsyncClient):
        """No vehicles in DB → not authenticated."""
        resp = await client.get("/api/auth/status")
        assert resp.status_code == 200
        assert resp.json() == {"authenticated": False, "vehicle_count": 0}

    async def test_authenticated(self, client: AsyncClient, db_session: AsyncSession):
        """Active vehicle in DB → authenticated."""
        vehicle = Vehicle(vin="5YJ3E1EAXKF000001", is_active=True)
        db_session.add(vehicle)
        await db_session.commit()

        resp = await client.get("/api/auth/status")
        assert resp.status_code == 200
        assert resp.json() == {"authenticated": True, "vehicle_count": 1}

    async def test_inactive_vehicle_not_counted(self, client: AsyncClient, db_session: AsyncSession):
        """Inactive vehicle should not count as authenticated."""
        vehicle = Vehicle(vin="5YJ3E1EAXKF000001", is_active=False)
        db_session.add(vehicle)
        await db_session.commit()

        resp = await client.get("/api/auth/status")
        assert resp.json()["authenticated"] is False


class TestLogout:
    async def test_logout_clears_tokens(self, client: AsyncClient, db_session: AsyncSession):
        """Logout sets is_active=False and clears tokens."""
        vehicle = Vehicle(
            vin="5YJ3E1EAXKF000001",
            is_active=True,
            access_token=encrypt_token("some.token"),
            refresh_token=encrypt_token("some.refresh"),
        )
        db_session.add(vehicle)
        await db_session.commit()

        resp = await client.delete("/api/auth/logout")
        assert resp.status_code == 200

        await db_session.refresh(vehicle)
        assert vehicle.is_active is False
        assert vehicle.access_token is None
        assert vehicle.refresh_token is None

    async def test_logout_empty_db(self, client: AsyncClient):
        """Logout with no vehicles should succeed gracefully."""
        resp = await client.delete("/api/auth/logout")
        assert resp.status_code == 200
