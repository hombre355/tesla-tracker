from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AppSettings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vehicles.id"))
    electricity_rate_per_kwh: Mapped[float] = mapped_column(Float, default=0.13)
    gas_price_per_gallon: Mapped[float] = mapped_column(Float, default=3.50)
    comparison_mpg: Mapped[float] = mapped_column(Float, default=30.0)
    sync_interval_minutes: Mapped[int] = mapped_column(Integer, default=5)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())

    vehicle: Mapped["Vehicle | None"] = relationship("Vehicle", back_populates="settings")
