from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ChargeSession(Base):
    __tablename__ = "charge_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    tesla_session_id: Mapped[str | None] = mapped_column(String, unique=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    location_name: Mapped[str | None] = mapped_column(String)
    charger_type: Mapped[str | None] = mapped_column(String)  # home, supercharger, destination, dc_fast
    kwh_added: Mapped[float | None] = mapped_column(Float)
    start_battery_pct: Mapped[float | None] = mapped_column(Float)
    end_battery_pct: Mapped[float | None] = mapped_column(Float)
    peak_power_kw: Mapped[float | None] = mapped_column(Float)
    electricity_cost_usd: Mapped[float | None] = mapped_column(Float)
    electricity_rate_used: Mapped[float | None] = mapped_column(Float)
    supercharger_cost_usd: Mapped[float | None] = mapped_column(Float)
    miles_added: Mapped[float | None] = mapped_column(Float)
    raw_data: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="charge_sessions")
