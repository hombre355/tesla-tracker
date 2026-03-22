from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChargeSessionOut(BaseModel):
    id: int
    vehicle_id: int
    started_at: datetime
    ended_at: Optional[datetime]
    location_name: Optional[str]
    charger_type: Optional[str]
    kwh_added: Optional[float]
    start_battery_pct: Optional[float]
    end_battery_pct: Optional[float]
    peak_power_kw: Optional[float]
    electricity_cost_usd: Optional[float]
    supercharger_cost_usd: Optional[float]
    miles_added: Optional[float]

    model_config = {"from_attributes": True}


class ChargeSummary(BaseModel):
    total_sessions: int
    total_kwh_added: float
    total_electricity_cost_usd: float
    total_supercharger_cost_usd: float
    avg_kwh_per_session: Optional[float]
    period: str
