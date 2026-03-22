from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VehicleOut(BaseModel):
    id: int
    vin: str
    display_name: Optional[str]
    model: Optional[str]
    color: Optional[str]
    pack_capacity_kwh: Optional[float]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
