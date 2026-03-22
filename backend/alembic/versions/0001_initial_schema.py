"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-22 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vin", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("color", sa.String(), nullable=True),
        sa.Column("pack_capacity_kwh", sa.Float(), nullable=True),
        sa.Column("access_token", sa.String(), nullable=True),
        sa.Column("refresh_token", sa.String(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vin"),
    )

    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=True),
        sa.Column("electricity_rate_per_kwh", sa.Float(), nullable=False),
        sa.Column("gas_price_per_gallon", sa.Float(), nullable=False),
        sa.Column("comparison_mpg", sa.Float(), nullable=False),
        sa.Column("sync_interval_minutes", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "trips",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("start_odometer_mi", sa.Float(), nullable=True),
        sa.Column("end_odometer_mi", sa.Float(), nullable=True),
        sa.Column("miles_driven", sa.Float(), nullable=True),
        sa.Column("start_battery_pct", sa.Float(), nullable=True),
        sa.Column("end_battery_pct", sa.Float(), nullable=True),
        sa.Column("start_battery_kwh", sa.Float(), nullable=True),
        sa.Column("end_battery_kwh", sa.Float(), nullable=True),
        sa.Column("kwh_used", sa.Float(), nullable=True),
        sa.Column("efficiency_mi_per_kwh", sa.Float(), nullable=True),
        sa.Column("start_location", sa.String(), nullable=True),
        sa.Column("end_location", sa.String(), nullable=True),
        sa.Column("raw_snapshot_start", sa.String(), nullable=True),
        sa.Column("raw_snapshot_end", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "charge_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("tesla_session_id", sa.String(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("location_name", sa.String(), nullable=True),
        sa.Column("charger_type", sa.String(), nullable=True),
        sa.Column("kwh_added", sa.Float(), nullable=True),
        sa.Column("start_battery_pct", sa.Float(), nullable=True),
        sa.Column("end_battery_pct", sa.Float(), nullable=True),
        sa.Column("peak_power_kw", sa.Float(), nullable=True),
        sa.Column("electricity_cost_usd", sa.Float(), nullable=True),
        sa.Column("electricity_rate_used", sa.Float(), nullable=True),
        sa.Column("supercharger_cost_usd", sa.Float(), nullable=True),
        sa.Column("miles_added", sa.Float(), nullable=True),
        sa.Column("raw_data", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tesla_session_id"),
    )

    op.create_table(
        "vehicle_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("captured_at", sa.DateTime(), nullable=False),
        sa.Column("shift_state", sa.String(), nullable=True),
        sa.Column("odometer_mi", sa.Float(), nullable=True),
        sa.Column("battery_level_pct", sa.Float(), nullable=True),
        sa.Column("battery_kwh_remaining", sa.Float(), nullable=True),
        sa.Column("charging_state", sa.String(), nullable=True),
        sa.Column("charge_energy_added", sa.Float(), nullable=True),
        sa.Column("charger_power", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("speed_mph", sa.Float(), nullable=True),
        sa.Column("raw_data", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("vehicle_snapshots")
    op.drop_table("charge_sessions")
    op.drop_table("trips")
    op.drop_table("settings")
    op.drop_table("vehicles")
