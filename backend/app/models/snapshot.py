from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VehicleSnapshot(Base):
    __tablename__ = "vehicle_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    shift_state: Mapped[str | None] = mapped_column(String)        # D, R, N, P, or None
    odometer_mi: Mapped[float | None] = mapped_column(Float)
    battery_level_pct: Mapped[float | None] = mapped_column(Float)
    battery_kwh_remaining: Mapped[float | None] = mapped_column(Float)
    charging_state: Mapped[str | None] = mapped_column(String)     # Charging, Complete, Disconnected
    charge_energy_added: Mapped[float | None] = mapped_column(Float)
    charger_power: Mapped[float | None] = mapped_column(Float)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    speed_mph: Mapped[float | None] = mapped_column(Float)
    raw_data: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="snapshots")
