import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charge_session import ChargeSession
from app.models.snapshot import VehicleSnapshot
from app.models.vehicle import Vehicle
from app.services import tesla_client, trip_detector


async def sync_vehicle(vehicle: Vehicle, db: AsyncSession) -> None:
    """Poll vehicle_data, store snapshot, detect trips, and check charging."""
    data = await tesla_client.get_vehicle_data(vehicle, db)
    if data is None:
        # Vehicle is asleep — skip
        return

    drive = data.get("drive_state", {})
    charge = data.get("charge_state", {})
    vehicle_state = data.get("vehicle_state", {})

    battery_pct = charge.get("battery_level")
    kwh_remaining = None
    if battery_pct is not None and vehicle.pack_capacity_kwh:
        kwh_remaining = round((battery_pct / 100.0) * vehicle.pack_capacity_kwh, 3)

    snapshot = VehicleSnapshot(
        vehicle_id=vehicle.id,
        captured_at=datetime.now(timezone.utc),
        shift_state=drive.get("shift_state"),
        odometer_mi=vehicle_state.get("odometer"),
        battery_level_pct=battery_pct,
        battery_kwh_remaining=kwh_remaining,
        charging_state=charge.get("charging_state"),
        charge_energy_added=charge.get("charge_energy_added"),
        charger_power=charge.get("charger_power"),
        latitude=drive.get("latitude"),
        longitude=drive.get("longitude"),
        speed_mph=drive.get("speed"),
        raw_data=json.dumps(data),
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)

    await trip_detector.process_snapshot(vehicle, snapshot, db)


async def sync_charging_history(vehicle: Vehicle, db: AsyncSession) -> int:
    """Pull charging history from Tesla API and upsert into charge_sessions. Returns new count."""
    sessions = await tesla_client.get_charging_history(vehicle, db)
    new_count = 0
    for s in sessions:
        session_id = s.get("din") or s.get("chargeSessionId") or str(s.get("timestamp", ""))
        if not session_id:
            continue

        existing = await db.execute(
            select(ChargeSession).where(ChargeSession.tesla_session_id == session_id)
        )
        if existing.scalar_one_or_none():
            continue

        charger_type = _classify_charger(s)
        session = ChargeSession(
            vehicle_id=vehicle.id,
            tesla_session_id=session_id,
            started_at=_parse_ts(s.get("chargeStartDateTime") or s.get("timestamp")),
            ended_at=_parse_ts(s.get("chargeStopDateTime")),
            location_name=s.get("siteLocationName") or s.get("chargerName"),
            charger_type=charger_type,
            kwh_added=s.get("energyAdded") or s.get("kwhAdded"),
            start_battery_pct=s.get("batteryLevelStart") or s.get("startBatteryLevel"),
            end_battery_pct=s.get("batteryLevelEnd") or s.get("endBatteryLevel"),
            peak_power_kw=s.get("peakPower"),
            supercharger_cost_usd=s.get("totalDue"),
            miles_added=s.get("milesAdded") or s.get("rangeAdded"),
            raw_data=json.dumps(s),
        )
        db.add(session)
        new_count += 1

    await db.commit()
    return new_count


def _classify_charger(session: dict) -> str:
    charger_type = (session.get("chargingType") or "").lower()
    if "supercharger" in charger_type or session.get("isSupercharger"):
        return "supercharger"
    power = session.get("peakPower") or 0
    if power >= 50:
        return "dc_fast"
    if power >= 7:
        return "destination"
    return "home"


def _parse_ts(val) -> datetime:
    if val is None:
        return datetime.now(timezone.utc)
    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(val, tz=timezone.utc)
    try:
        return datetime.fromisoformat(str(val).replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


async def sync_all_vehicles(db: AsyncSession) -> None:
    result = await db.execute(select(Vehicle).where(Vehicle.is_active == True))
    vehicles = result.scalars().all()
    for vehicle in vehicles:
        try:
            await sync_vehicle(vehicle, db)
        except Exception as e:
            print(f"[sync] Error syncing vehicle {vehicle.vin}: {e}")
