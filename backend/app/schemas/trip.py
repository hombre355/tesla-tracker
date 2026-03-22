from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TripOut(BaseModel):
    id: int
    vehicle_id: int
    started_at: datetime
    ended_at: Optional[datetime]
    miles_driven: Optional[float]
    kwh_used: Optional[float]
    efficiency_mi_per_kwh: Optional[float]
    start_battery_pct: Optional[float]
    end_battery_pct: Optional[float]
    start_location: Optional[str]
    end_location: Optional[str]

    model_config = {"from_attributes": True}


class TripSummary(BaseModel):
    total_trips: int
    total_miles: float
    total_kwh_used: float
    avg_efficiency_mi_per_kwh: Optional[float]
    period: str  # "week", "month", "all"
