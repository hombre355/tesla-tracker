from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleOut
from app.services.sync_service import sync_vehicle

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleOut])
async def list_vehicles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle).where(Vehicle.is_active == True))
    return result.scalars().all()


@router.get("/{vin}", response_model=VehicleOut)
async def get_vehicle(vin: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle).where(Vehicle.vin == vin))
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.post("/sync")
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle).where(Vehicle.is_active == True))
    vehicles = result.scalars().all()
    synced = []
    for v in vehicles:
        try:
            await sync_vehicle(v, db)
            synced.append(v.vin)
        except Exception as e:
            synced.append(f"{v.vin} (error: {e})")
    return {"synced": synced}
