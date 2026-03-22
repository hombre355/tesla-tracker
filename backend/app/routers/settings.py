from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.settings import AppSettings
from app.schemas.settings import SettingsOut, SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])


async def _get_or_create(db: AsyncSession) -> AppSettings:
    result = await db.execute(select(AppSettings).where(AppSettings.vehicle_id.is_(None)).limit(1))
    s = result.scalar_one_or_none()
    if s is None:
        s = AppSettings()
        db.add(s)
        await db.commit()
        await db.refresh(s)
    return s


@router.get("", response_model=SettingsOut)
async def get_settings(db: AsyncSession = Depends(get_db)):
    return await _get_or_create(db)


@router.put("", response_model=SettingsOut)
async def update_settings(body: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    s = await _get_or_create(db)
    if body.electricity_rate_per_kwh is not None:
        s.electricity_rate_per_kwh = body.electricity_rate_per_kwh
    if body.gas_price_per_gallon is not None:
        s.gas_price_per_gallon = body.gas_price_per_gallon
    if body.comparison_mpg is not None:
        s.comparison_mpg = body.comparison_mpg
    if body.sync_interval_minutes is not None:
        s.sync_interval_minutes = body.sync_interval_minutes
        from app.tasks.scheduler import start_scheduler
        start_scheduler(body.sync_interval_minutes)
    await db.commit()
    await db.refresh(s)
    return s
