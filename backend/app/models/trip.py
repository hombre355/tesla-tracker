from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    start_odometer_mi: Mapped[float | None] = mapped_column(Float)
    end_odometer_mi: Mapped[float | None] = mapped_column(Float)
    miles_driven: Mapped[float | None] = mapped_column(Float)
    start_battery_pct: Mapped[float | None] = mapped_column(Float)
    end_battery_pct: Mapped[float | None] = mapped_column(Float)
    start_battery_kwh: Mapped[float | None] = mapped_column(Float)
    end_battery_kwh: Mapped[float | None] = mapped_column(Float)
    kwh_used: Mapped[float | None] = mapped_column(Float)
    efficiency_mi_per_kwh: Mapped[float | None] = mapped_column(Float)
    start_location: Mapped[str | None] = mapped_column(String)    # JSON {"lat": x, "lon": y}
    end_location: Mapped[str | None] = mapped_column(String)      # JSON {"lat": x, "lon": y}
    raw_snapshot_start: Mapped[str | None] = mapped_column(String)
    raw_snapshot_end: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="trips")
