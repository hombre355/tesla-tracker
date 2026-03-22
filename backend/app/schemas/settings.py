from typing import Optional

from pydantic import BaseModel, Field


class SettingsOut(BaseModel):
    id: int
    vehicle_id: Optional[int]
    electricity_rate_per_kwh: float
    gas_price_per_gallon: float
    comparison_mpg: float
    sync_interval_minutes: int

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    electricity_rate_per_kwh: Optional[float] = Field(None, gt=0)
    gas_price_per_gallon: Optional[float] = Field(None, gt=0)
    comparison_mpg: Optional[float] = Field(None, gt=0)
    sync_interval_minutes: Optional[int] = Field(None, ge=1, le=60)
