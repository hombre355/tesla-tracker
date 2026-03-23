"""Tests for trip_detector.py — unit tests for helpers + integration tests for process_snapshot."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.snapshot import VehicleSnapshot
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.services.trip_detector import _kwh_from_pct, process_snapshot


# ---------------------------------------------------------------------------
# Unit tests: _kwh_from_pct
# ---------------------------------------------------------------------------


class TestKwhFromPct:
    def test_nominal(self):
        assert _kwh_from_pct(80.0, 75.0) == pytest.approx(60.0)

    def test_full_battery(self):
        assert _kwh_from_pct(100.0, 82.0) == pytest.approx(82.0)

    def test_empty_battery(self):
        assert _kwh_from_pct(0.0, 75.0) == pytest.approx(0.0)

    def test_none_pct(self):
        assert _kwh_from_pct(None, 75.0) is None

    def test_none_pack(self):
        assert _kwh_from_pct(80.0, None) is None

    def test_both_none(self):
        assert _kwh_from_pct(None, None) is None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_vehicle() -> Vehicle:
    return Vehicle(vin="5YJ3E1EAXKF000001", pack_capacity_kwh=75.0, is_active=True)


def _snapshot(vehicle_id: int, shift_state: str | None, odometer: float, battery_pct: float, ts: datetime) -> VehicleSnapshot:
    return VehicleSnapshot(
        vehicle_id=vehicle_id,
        captured_at=ts,
        shift_state=shift_state,
        odometer_mi=odometer,
        battery_level_pct=battery_pct,
    )


def _ts(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0)  # naive UTC — matches DateTime (no tz) columns


# ---------------------------------------------------------------------------
# Integration tests: process_snapshot
# ---------------------------------------------------------------------------


async def _trip_count(db: AsyncSession, vehicle_id: int) -> int:
    result = await db.execute(select(Trip).where(Trip.vehicle_id == vehicle_id))
    return len(result.scalars().all())


async def _open_trip(db: AsyncSession, vehicle_id: int) -> Trip | None:
    result = await db.execute(
        select(Trip).where(Trip.vehicle_id == vehicle_id).where(Trip.ended_at.is_(None))
    )
    return result.scalar_one_or_none()


class TestProcessSnapshot:
    async def test_first_snapshot_no_trip(self, db_session: AsyncSession):
        """Single snapshot with no previous — nothing should happen."""
        vehicle = _make_vehicle()
        db_session.add(vehicle)
        await db_session.commit()
        await db_session.refresh(vehicle)

        snap = _snapshot(vehicle.id, "P", 10000.0, 80.0, _ts(8))
        db_session.add(snap)
        await db_session.commit()
        await db_session.refresh(snap)

        await process_snapshot(vehicle, snap, db_session)
        assert await _trip_count(db_session, vehicle.id) == 0

    async def test_parked_to_driving_creates_trip(self, db_session: AsyncSession):
        """P → D should open a new trip."""
        vehicle = _make_vehicle()
        db_session.add(vehicle)
        await db_session.commit()
        await db_session.refresh(vehicle)

        prev = _snapshot(vehicle.id, "P", 10000.0, 90.0, _ts(8))
        db_session.add(prev)
        await db_session.commit()

        curr = _snapshot(vehicle.id, "D", 10000.0, 89.5, _ts(9))
        db_session.add(curr)
        await db_session.commit()
        await db_session.refresh(curr)

        await process_snapshot(vehicle, curr, db_session)

        trip = await _open_trip(db_session, vehicle.id)
        assert trip is not None
        assert trip.ended_at is None
        assert trip.start_battery_pct == pytest.approx(89.5)

    async def test_driving_to_parked_closes_trip(self, db_session: AsyncSession):
        """D → P should close the open trip with computed fields."""
        vehicle = _make_vehicle()
        db_session.add(vehicle)
        await db_session.commit()
        await db_session.refresh(vehicle)

        # Snapshot 1: parked
        s1 = _snapshot(vehicle.id, "P", 10000.0, 90.0, _ts(7))
        db_session.add(s1)
        await db_session.commit()

        # Snapshot 2: driving → opens trip
        s2 = _snapshot(vehicle.id, "D", 10000.0, 90.0, _ts(8))
        db_session.add(s2)
        await db_session.commit()
        await db_session.refresh(s2)
        await process_snapshot(vehicle, s2, db_session)

        # Snapshot 3: parked → closes trip
        s3 = _snapshot(vehicle.id, "P", 10010.0, 80.0, _ts(9))
        db_session.add(s3)
        await db_session.commit()
        await db_session.refresh(s3)
        await process_snapshot(vehicle, s3, db_session)

        result = await db_session.execute(select(Trip).where(Trip.vehicle_id == vehicle.id))
        trip = result.scalar_one()

        assert trip.ended_at is not None
        assert trip.miles_driven == pytest.approx(10.0)
        # 90% → 80% of 75 kWh = 7.5 kWh used
        assert trip.kwh_used == pytest.approx(7.5)
        # 10 miles / 7.5 kWh ≈ 1.333 mi/kWh
        assert trip.efficiency_mi_per_kwh == pytest.approx(1.333, rel=1e-2)

    async def test_still_driving_no_new_trip(self, db_session: AsyncSession):
        """D → D should not open a second trip."""
        vehicle = _make_vehicle()
        db_session.add(vehicle)
        await db_session.commit()
        await db_session.refresh(vehicle)

        s1 = _snapshot(vehicle.id, "P", 10000.0, 90.0, _ts(7))
        db_session.add(s1)
        await db_session.commit()

        s2 = _snapshot(vehicle.id, "D", 10000.0, 90.0, _ts(8))
        db_session.add(s2)
        await db_session.commit()
        await db_session.refresh(s2)
        await process_snapshot(vehicle, s2, db_session)

        s3 = _snapshot(vehicle.id, "D", 10005.0, 85.0, _ts(9))
        db_session.add(s3)
        await db_session.commit()
        await db_session.refresh(s3)
        await process_snapshot(vehicle, s3, db_session)

        assert await _trip_count(db_session, vehicle.id) == 1
        assert await _open_trip(db_session, vehicle.id) is not None

    async def test_still_parked_no_trip(self, db_session: AsyncSession):
        """P → P should not create any trips."""
        vehicle = _make_vehicle()
        db_session.add(vehicle)
        await db_session.commit()
        await db_session.refresh(vehicle)

        s1 = _snapshot(vehicle.id, "P", 10000.0, 80.0, _ts(8))
        db_session.add(s1)
        await db_session.commit()

        s2 = _snapshot(vehicle.id, "P", 10000.0, 80.0, _ts(9))
        db_session.add(s2)
        await db_session.commit()
        await db_session.refresh(s2)
        await process_snapshot(vehicle, s2, db_session)

        assert await _trip_count(db_session, vehicle.id) == 0

    async def test_driving_to_parked_no_open_trip_is_graceful(self, db_session: AsyncSession):
        """D → P with no open trip should not raise."""
        vehicle = _make_vehicle()
        db_session.add(vehicle)
        await db_session.commit()
        await db_session.refresh(vehicle)

        s1 = _snapshot(vehicle.id, "D", 10000.0, 80.0, _ts(8))
        db_session.add(s1)
        await db_session.commit()

        s2 = _snapshot(vehicle.id, "P", 10010.0, 70.0, _ts(9))
        db_session.add(s2)
        await db_session.commit()
        await db_session.refresh(s2)

        # Should not raise
        await process_snapshot(vehicle, s2, db_session)
        assert await _trip_count(db_session, vehicle.id) == 0

    async def test_missing_odometer_efficiency_is_none(self, db_session: AsyncSession):
        """Trip with missing odometer should have None miles_driven and efficiency."""
        vehicle = _make_vehicle()
        db_session.add(vehicle)
        await db_session.commit()
        await db_session.refresh(vehicle)

        s1 = _snapshot(vehicle.id, "P", None, 90.0, _ts(7))
        db_session.add(s1)
        await db_session.commit()

        s2 = _snapshot(vehicle.id, "D", None, 90.0, _ts(8))
        db_session.add(s2)
        await db_session.commit()
        await db_session.refresh(s2)
        await process_snapshot(vehicle, s2, db_session)

        s3 = _snapshot(vehicle.id, "P", None, 80.0, _ts(9))
        db_session.add(s3)
        await db_session.commit()
        await db_session.refresh(s3)
        await process_snapshot(vehicle, s3, db_session)

        result = await db_session.execute(select(Trip).where(Trip.vehicle_id == vehicle.id))
        trip = result.scalar_one()
        assert trip.miles_driven is None
        assert trip.efficiency_mi_per_kwh is None
