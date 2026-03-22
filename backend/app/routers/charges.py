from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.charge_session import ChargeSession
from app.schemas.charge_session import ChargeSummary, ChargeSessionOut

router = APIRouter(prefix="/api/charges", tags=["charges"])


@router.get("", response_model=list[ChargeSessionOut])
async def list_charges(
    vin: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    charger_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(ChargeSession).order_by(ChargeSession.started_at.desc())
    if vin:
        from app.models.vehicle import Vehicle
        result = await db.execute(select(Vehicle).where(Vehicle.vin == vin))
        vehicle = result.scalar_one_or_none()
        if vehicle:
            query = query.where(ChargeSession.vehicle_id == vehicle.id)
    if charger_type:
        query = query.where(ChargeSession.charger_type == charger_type)
    if start_date:
        query = query.where(ChargeSession.started_at >= start_date)
    if end_date:
        from datetime import datetime, time
        query = query.where(ChargeSession.started_at <= datetime.combine(end_date, time.max))
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stats/summary", response_model=ChargeSummary)
async def charge_summary(
    vin: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(
        func.count(ChargeSession.id),
        func.coalesce(func.sum(ChargeSession.kwh_added), 0),
        func.coalesce(func.sum(ChargeSession.electricity_cost_usd), 0),
        func.coalesce(func.sum(ChargeSession.supercharger_cost_usd), 0),
        func.avg(ChargeSession.kwh_added),
    )
    if vin:
        from app.models.vehicle import Vehicle
        result = await db.execute(select(Vehicle).where(Vehicle.vin == vin))
        vehicle = result.scalar_one_or_none()
        if vehicle:
            query = query.where(ChargeSession.vehicle_id == vehicle.id)
    if start_date:
        query = query.where(ChargeSession.started_at >= start_date)
    if end_date:
        from datetime import datetime, time
        query = query.where(ChargeSession.started_at <= datetime.combine(end_date, time.max))

    row = (await db.execute(query)).one()
    return ChargeSummary(
        total_sessions=row[0],
        total_kwh_added=float(row[1]),
        total_electricity_cost_usd=float(row[2]),
        total_supercharger_cost_usd=float(row[3]),
        avg_kwh_per_session=float(row[4]) if row[4] else None,
        period="custom",
    )


@router.post("/sync")
async def sync_charges(db: AsyncSession = Depends(get_db)):
    from app.models.vehicle import Vehicle
    from app.services.sync_service import sync_charging_history

    result = await db.execute(select(Vehicle).where(Vehicle.is_active == True))
    vehicles = result.scalars().all()
    total = 0
    for v in vehicles:
        count = await sync_charging_history(v, db)
        total += count
    return {"new_sessions": total}


@router.get("/{charge_id}", response_model=ChargeSessionOut)
async def get_charge(charge_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChargeSession).where(ChargeSession.id == charge_id))
    session = result.scalar_one_or_none()
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Charge session not found")
    return session
