"""Tests for GET /api/settings and PUT /api/settings."""

import pytest
from httpx import AsyncClient


class TestGetSettings:
    async def test_defaults_on_empty_db(self, client: AsyncClient):
        """GET settings with empty DB should return default values."""
        resp = await client.get("/api/settings")
        assert resp.status_code == 200
        data = resp.json()
        assert data["electricity_rate_per_kwh"] == pytest.approx(0.13)
        assert data["gas_price_per_gallon"] == pytest.approx(3.50)
        assert data["comparison_mpg"] == pytest.approx(30.0)
        assert data["sync_interval_minutes"] == 5

    async def test_get_is_idempotent(self, client: AsyncClient):
        """Calling GET twice should return the same row (not create duplicates)."""
        resp1 = await client.get("/api/settings")
        resp2 = await client.get("/api/settings")
        assert resp1.json()["id"] == resp2.json()["id"]


class TestUpdateSettings:
    async def test_update_electricity_rate(self, client: AsyncClient):
        resp = await client.put(
            "/api/settings", json={"electricity_rate_per_kwh": 0.20}
        )
        assert resp.status_code == 200
        assert resp.json()["electricity_rate_per_kwh"] == pytest.approx(0.20)

    async def test_update_all_fields(self, client: AsyncClient):
        payload = {
            "electricity_rate_per_kwh": 0.18,
            "gas_price_per_gallon": 4.25,
            "comparison_mpg": 35.0,
            "sync_interval_minutes": 10,
        }
        resp = await client.put("/api/settings", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["electricity_rate_per_kwh"] == pytest.approx(0.18)
        assert data["gas_price_per_gallon"] == pytest.approx(4.25)
        assert data["comparison_mpg"] == pytest.approx(35.0)
        assert data["sync_interval_minutes"] == 10

    async def test_update_persists(self, client: AsyncClient):
        """Change made via PUT should be visible on the next GET."""
        await client.put("/api/settings", json={"electricity_rate_per_kwh": 0.25})
        resp = await client.get("/api/settings")
        assert resp.json()["electricity_rate_per_kwh"] == pytest.approx(0.25)

    # --- Validation edge cases (should all return 422) ---

    async def test_electricity_rate_zero(self, client: AsyncClient):
        resp = await client.put("/api/settings", json={"electricity_rate_per_kwh": 0})
        assert resp.status_code == 422

    async def test_electricity_rate_negative(self, client: AsyncClient):
        resp = await client.put("/api/settings", json={"electricity_rate_per_kwh": -0.10})
        assert resp.status_code == 422

    async def test_gas_price_zero(self, client: AsyncClient):
        resp = await client.put("/api/settings", json={"gas_price_per_gallon": 0})
        assert resp.status_code == 422

    async def test_comparison_mpg_zero(self, client: AsyncClient):
        resp = await client.put("/api/settings", json={"comparison_mpg": 0})
        assert resp.status_code == 422

    async def test_sync_interval_zero(self, client: AsyncClient):
        resp = await client.put("/api/settings", json={"sync_interval_minutes": 0})
        assert resp.status_code == 422

    async def test_sync_interval_above_max(self, client: AsyncClient):
        resp = await client.put("/api/settings", json={"sync_interval_minutes": 61})
        assert resp.status_code == 422

    async def test_sync_interval_min_boundary(self, client: AsyncClient):
        """sync_interval_minutes=1 is the lower boundary — should succeed."""
        resp = await client.put("/api/settings", json={"sync_interval_minutes": 1})
        assert resp.status_code == 200
        assert resp.json()["sync_interval_minutes"] == 1

    async def test_sync_interval_max_boundary(self, client: AsyncClient):
        """sync_interval_minutes=60 is the upper boundary — should succeed."""
        resp = await client.put("/api/settings", json={"sync_interval_minutes": 60})
        assert resp.status_code == 200
        assert resp.json()["sync_interval_minutes"] == 60
