from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.trip import Trip
from app.schemas.trip import TripOut, TripSummary

router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.get("", response_model=list[TripOut])
async def list_trips(
    vin: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Trip).order_by(Trip.started_at.desc())
    if vin:
        from app.models.vehicle import Vehicle
        result = await db.execute(select(Vehicle).where(Vehicle.vin == vin))
        vehicle = result.scalar_one_or_none()
        if vehicle:
            query = query.where(Trip.vehicle_id == vehicle.id)
    if start_date:
        query = query.where(Trip.started_at >= start_date)
    if end_date:
        from datetime import datetime, time
        query = query.where(Trip.started_at <= datetime.combine(end_date, time.max))
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/stats/summary", response_model=TripSummary)
async def trip_summary(
    vin: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(
        func.count(Trip.id),
        func.coalesce(func.sum(Trip.miles_driven), 0),
        func.coalesce(func.sum(Trip.kwh_used), 0),
        func.avg(Trip.efficiency_mi_per_kwh),
    ).where(Trip.ended_at.isnot(None))

    if vin:
        from app.models.vehicle import Vehicle
        result = await db.execute(select(Vehicle).where(Vehicle.vin == vin))
        vehicle = result.scalar_one_or_none()
        if vehicle:
            query = query.where(Trip.vehicle_id == vehicle.id)
    if start_date:
        query = query.where(Trip.started_at >= start_date)
    if end_date:
        from datetime import datetime, time
        query = query.where(Trip.started_at <= datetime.combine(end_date, time.max))

    row = (await db.execute(query)).one()
    return TripSummary(
        total_trips=row[0],
        total_miles=float(row[1]),
        total_kwh_used=float(row[2]),
        avg_efficiency_mi_per_kwh=float(row[3]) if row[3] else None,
        period="custom",
    )


@router.get("/{trip_id}", response_model=TripOut)
async def get_trip(trip_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Trip).where(Trip.id == trip_id))
    trip = result.scalar_one_or_none()
    if not trip:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
