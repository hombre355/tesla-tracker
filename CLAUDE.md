# Tesla Tracker

Personal web app to track Tesla Model 3 driving energy usage, charging costs, and gas car cost comparison.

## Tech Stack

**Backend**: Python FastAPI + SQLite (aiosqlite) + SQLAlchemy 2.0+ + APScheduler + httpx
**Frontend**: React 18 + Vite + TypeScript + Tailwind CSS + Recharts + TanStack Query + Zustand

## Run Commands

```bash
# Backend (port 8000)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Frontend (port 5173)
cd frontend && npm run dev
```

API docs: http://localhost:8000/docs
Frontend proxies `/api` requests to backend via Vite config.

## Project Structure

```
backend/app/
  config.py          # Pydantic settings (loads .env)
  database.py        # SQLAlchemy async engine
  main.py            # FastAPI app + lifespan (startup DB, scheduler)
  models/            # SQLAlchemy ORM models
  routers/           # API route handlers
  schemas/           # Pydantic request/response models
  services/          # Business logic
    tesla_client.py  # Tesla Fleet API wrapper (OAuth, token refresh, encryption)
    trip_detector.py # Detects trip start/end from snapshot shift_state transitions
    sync_service.py  # Polls vehicle data, syncs charging history
    cost_calculator.py
  tasks/scheduler.py # APScheduler background jobs

frontend/src/
  api/               # Axios API client methods
  components/        # Charts, layout, common UI
  hooks/             # useTrips, useCharges, useSettings
  pages/             # Dashboard, Trips, Charging, Comparison, Settings, Connect
  store/authStore.ts # Zustand auth state
  utils/formatters.ts
  App.tsx            # React Router config
```

## Environment Setup

Copy `backend/.env.example` to `backend/.env` and fill in:

```
TESLA_CLIENT_ID=          # From developer.tesla.com
TESLA_CLIENT_SECRET=
TESLA_REDIRECT_URI=http://localhost:8000/api/auth/callback
TESLA_AUDIENCE=https://fleet-api.prd.na.vn.cloud.tesla.com
ENCRYPTION_KEY=           # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
DATABASE_URL=sqlite+aiosqlite:///./tesla_tracker.db
FRONTEND_URL=http://localhost:5173
```

## Database (SQLite, 5 tables)

- **vehicles** — VIN, OAuth tokens (Fernet-encrypted), battery capacity
- **trips** — start/end odometer, kWh used, efficiency (mi/kWh), locations
- **charge_sessions** — kWh added, charger type, cost (home = kWh × rate; supercharger from Tesla billing)
- **vehicle_snapshots** — Raw 5-min poll data (shift_state, odometer, battery %, GPS)
- **settings** — electricity rate, gas price, comparison MPG, sync interval

## Key Architecture Notes

**Trip detection**: No native Tesla trip API. Backend polls `vehicle_data` every 5 minutes and watches `shift_state` transitions — P/null → D/R = trip start, D/R → P/null = trip end. Trips under 5 minutes may be missed.

**Charging sync**: Pulled from Tesla's `GET /api/1/dx/charging/history`. Home charging cost = kWh × electricity rate from settings. Supercharger cost comes from Tesla billing data.

**Token storage**: Access/refresh tokens stored encrypted (Fernet) in the `vehicles` table.

**Charger classification** by peak power: ≥50 kW = dc_fast, ≥7 kW = destination, <7 kW = home.

## Critical Constraint

**SQLAlchemy must be >=2.0.48** — older versions have a Union typing incompatibility with Python 3.14. Do not downgrade.

## API Routes Summary

```
GET  /api/auth/login          # Redirect to Tesla OAuth
GET  /api/auth/callback       # OAuth callback
GET  /api/auth/status         # {authenticated, vehicle_count}
GET  /api/vehicles            # List active vehicles
POST /api/vehicles/sync       # Trigger immediate sync
GET  /api/trips               # List trips (paginated, filterable)
GET  /api/trips/stats/summary # Aggregated stats
GET  /api/charges             # List charge sessions
POST /api/charges/sync        # Pull latest from Tesla API
GET  /api/stats/dashboard     # Monthly KPIs
GET  /api/stats/comparison    # Monthly Tesla vs gas cost
GET  /api/settings            # Fetch settings
PUT  /api/settings            # Update rates/intervals
GET  /health
```
