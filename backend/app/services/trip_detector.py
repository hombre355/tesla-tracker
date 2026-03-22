import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.snapshot import VehicleSnapshot
from app.models.trip import Trip
from app.models.vehicle import Vehicle

DRIVING_STATES = {"D", "R", "N"}


def _kwh_from_pct(pct: Optional[float], pack_kwh: Optional[float]) -> Optional[float]:
    if pct is None or pack_kwh is None:
        return None
    return round((pct / 100.0) * pack_kwh, 3)


async def process_snapshot(
    vehicle: Vehicle,
    snapshot: VehicleSnapshot,
    db: AsyncSession,
) -> None:
    """
    Compare the new snapshot against the previous one to detect trip start/end.
    Writes new Trip rows or closes open trips as needed.
    """
    # Get the previous snapshot
    result = await db.execute(
        select(VehicleSnapshot)
        .where(VehicleSnapshot.vehicle_id == vehicle.id)
        .where(VehicleSnapshot.id != snapshot.id)
        .order_by(VehicleSnapshot.captured_at.desc())
        .limit(1)
    )
    prev = result.scalar_one_or_none()

    prev_driving = prev is not None and prev.shift_state in DRIVING_STATES
    curr_driving = snapshot.shift_state in DRIVING_STATES

    # Transition: parked → driving = trip start
    if not prev_driving and curr_driving:
        trip = Trip(
            vehicle_id=vehicle.id,
            started_at=snapshot.captured_at,
            start_odometer_mi=snapshot.odometer_mi,
            start_battery_pct=snapshot.battery_level_pct,
            start_battery_kwh=_kwh_from_pct(snapshot.battery_level_pct, vehicle.pack_capacity_kwh),
            start_location=json.dumps({"lat": snapshot.latitude, "lon": snapshot.longitude})
            if snapshot.latitude
            else None,
            raw_snapshot_start=snapshot.raw_data,
        )
        db.add(trip)
        await db.commit()

    # Transition: driving → parked = trip end
    elif prev_driving and not curr_driving:
        # Find the most recent open trip for this vehicle
        result = await db.execute(
            select(Trip)
            .where(Trip.vehicle_id == vehicle.id)
            .where(Trip.ended_at.is_(None))
            .order_by(Trip.started_at.desc())
            .limit(1)
        )
        open_trip = result.scalar_one_or_none()
        if open_trip:
            end_kwh = _kwh_from_pct(snapshot.battery_level_pct, vehicle.pack_capacity_kwh)
            miles = None
            if open_trip.start_odometer_mi and snapshot.odometer_mi:
                miles = round(snapshot.odometer_mi - open_trip.start_odometer_mi, 2)

            kwh_used = None
            if open_trip.start_battery_kwh is not None and end_kwh is not None:
                kwh_used = round(open_trip.start_battery_kwh - end_kwh, 3)

            efficiency = None
            if miles and kwh_used and kwh_used > 0:
                efficiency = round(miles / kwh_used, 3)

            open_trip.ended_at = snapshot.captured_at
            open_trip.end_odometer_mi = snapshot.odometer_mi
            open_trip.end_battery_pct = snapshot.battery_level_pct
            open_trip.end_battery_kwh = end_kwh
            open_trip.miles_driven = miles
            open_trip.kwh_used = kwh_used
            open_trip.efficiency_mi_per_kwh = efficiency
            open_trip.end_location = (
                json.dumps({"lat": snapshot.latitude, "lon": snapshot.longitude})
                if snapshot.latitude
                else None
            )
            open_trip.raw_snapshot_end = snapshot.raw_data
            await db.commit()
