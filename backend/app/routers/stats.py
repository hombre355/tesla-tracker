from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.charge_session import ChargeSession
from app.models.settings import AppSettings
from app.models.trip import Trip
from app.services.cost_calculator import electricity_cost, gas_equivalent_cost, savings

router = APIRouter(prefix="/api/stats", tags=["stats"])


async def _get_settings(db: AsyncSession) -> AppSettings:
    result = await db.execute(select(AppSettings).where(AppSettings.vehicle_id.is_(None)).limit(1))
    s = result.scalar_one_or_none()
    if s is None:
        s = AppSettings()
    return s


@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    s = await _get_settings(db)

    # This month trips
    trip_row = (
        await db.execute(
            select(
                func.count(Trip.id),
                func.coalesce(func.sum(Trip.miles_driven), 0),
                func.coalesce(func.sum(Trip.kwh_used), 0),
            ).where(Trip.started_at >= month_start, Trip.ended_at.isnot(None))
        )
    ).one()

    # This month charges
    charge_row = (
        await db.execute(
            select(
                func.count(ChargeSession.id),
                func.coalesce(func.sum(ChargeSession.kwh_added), 0),
                func.coalesce(func.sum(ChargeSession.electricity_cost_usd), 0),
            ).where(ChargeSession.started_at >= month_start)
        )
    ).one()

    total_miles = float(trip_row[1])
    total_kwh_used = float(trip_row[2])
    elec_cost = electricity_cost(total_kwh_used, s.electricity_rate_per_kwh)
    gas_cost = gas_equivalent_cost(total_miles, s.comparison_mpg, s.gas_price_per_gallon)

    return {
        "this_month": {
            "trips": trip_row[0],
            "miles_driven": total_miles,
            "kwh_used": total_kwh_used,
            "electricity_cost_usd": elec_cost,
            "gas_equivalent_cost_usd": gas_cost,
            "savings_usd": savings(elec_cost, gas_cost),
        },
        "charging": {
            "sessions": charge_row[0],
            "kwh_added": float(charge_row[1]),
            "total_cost_usd": float(charge_row[2]),
        },
    }


@router.get("/comparison")
async def cost_comparison(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    s = await _get_settings(db)
    query = select(Trip.started_at, Trip.miles_driven, Trip.kwh_used).where(
        Trip.ended_at.isnot(None), Trip.miles_driven.isnot(None)
    )
    if start_date:
        query = query.where(Trip.started_at >= start_date)
    if end_date:
        query = query.where(Trip.started_at <= datetime.combine(end_date, time.max))

    rows = (await db.execute(query)).all()

    # Group by month
    monthly: dict[str, dict] = {}
    for started_at, miles, kwh in rows:
        if miles is None:
            continue
        key = started_at.strftime("%Y-%m") if hasattr(started_at, "strftime") else str(started_at)[:7]
        if key not in monthly:
            monthly[key] = {"miles": 0.0, "kwh": 0.0}
        monthly[key]["miles"] += miles or 0
        monthly[key]["kwh"] += kwh or 0

    result = []
    cumulative_savings = 0.0
    for month in sorted(monthly.keys()):
        m = monthly[month]
        elec = electricity_cost(m["kwh"], s.electricity_rate_per_kwh)
        gas = gas_equivalent_cost(m["miles"], s.comparison_mpg, s.gas_price_per_gallon)
        saved = savings(elec, gas)
        cumulative_savings += saved
        result.append({
            "month": month,
            "miles": round(m["miles"], 1),
            "kwh_used": round(m["kwh"], 2),
            "electricity_cost_usd": elec,
            "gas_equivalent_cost_usd": gas,
            "savings_usd": saved,
            "cumulative_savings_usd": round(cumulative_savings, 2),
        })
    return result


@router.get("/efficiency/trend")
async def efficiency_trend(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        await db.execute(
            select(Trip.started_at, Trip.miles_driven, Trip.kwh_used, Trip.efficiency_mi_per_kwh)
            .where(Trip.started_at >= since, Trip.ended_at.isnot(None))
            .order_by(Trip.started_at)
        )
    ).all()
    return [
        {
            "date": r[0].strftime("%Y-%m-%d") if hasattr(r[0], "strftime") else str(r[0])[:10],
            "miles": r[1],
            "kwh_used": r[2],
            "efficiency_mi_per_kwh": r[3],
        }
        for r in rows
    ]


@router.get("/charging/trend")
async def charging_trend(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        await db.execute(
            select(ChargeSession.started_at, ChargeSession.kwh_added, ChargeSession.electricity_cost_usd, ChargeSession.charger_type)
            .where(ChargeSession.started_at >= since)
            .order_by(ChargeSession.started_at)
        )
    ).all()
    return [
        {
            "date": r[0].strftime("%Y-%m-%d") if hasattr(r[0], "strftime") else str(r[0])[:10],
            "kwh_added": r[1],
            "cost_usd": r[2],
            "charger_type": r[3],
        }
        for r in rows
    ]
