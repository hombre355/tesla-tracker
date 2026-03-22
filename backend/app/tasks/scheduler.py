from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.database import AsyncSessionLocal
from app.services.sync_service import sync_all_vehicles

scheduler = AsyncIOScheduler()


async def _run_sync():
    async with AsyncSessionLocal() as db:
        await sync_all_vehicles(db)


def start_scheduler(interval_minutes: int = 5):
    if scheduler.running:
        scheduler.remove_all_jobs()
    scheduler.add_job(
        _run_sync,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="vehicle_sync",
        replace_existing=True,
    )
    if not scheduler.running:
        scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
