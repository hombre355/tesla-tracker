from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vin: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String)
    model: Mapped[str | None] = mapped_column(String)
    color: Mapped[str | None] = mapped_column(String)
    pack_capacity_kwh: Mapped[float | None] = mapped_column(Float)  # 57.5, 75, etc.
    access_token: Mapped[str | None] = mapped_column(String)       # encrypted
    refresh_token: Mapped[str | None] = mapped_column(String)      # encrypted
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())

    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="vehicle")
    charge_sessions: Mapped[list["ChargeSession"]] = relationship("ChargeSession", back_populates="vehicle")
    snapshots: Mapped[list["VehicleSnapshot"]] = relationship("VehicleSnapshot", back_populates="vehicle")
    settings: Mapped[list["AppSettings"]] = relationship("AppSettings", back_populates="vehicle")
