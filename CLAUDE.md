# Tesla Tracker

Personal web app to track Tesla Model 3 driving energy usage, charging costs, and gas car cost comparison.

## Working Rules

After every code change, update this file (CLAUDE.md) and README.md to reflect any additions, removals, or modifications to the tech stack, architecture, API routes, environment variables, or deployment process.

## Tech Stack

**Backend**: Python FastAPI + PostgreSQL (asyncpg) + SQLAlchemy 2.0+ + Alembic + APScheduler + httpx
**Frontend**: React 18 + Vite + TypeScript + Tailwind CSS + Recharts + TanStack Query + Zustand

## Run Commands

```bash
# Backend (port 8000)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Frontend (port 5173)
cd frontend && npm run dev

# Full stack via Docker (local dev)
docker compose up --build
```

API docs: http://localhost:8000/docs
Frontend proxies `/api` requests to backend via Vite config.

## Project Structure

```
backend/app/
  config.py          # Pydantic settings (loads .env) — no Tesla developer credentials needed
  database.py        # SQLAlchemy async engine
  main.py            # FastAPI app + lifespan (scheduler only — Alembic handles schema)
  models/            # SQLAlchemy ORM models
  routers/           # API route handlers
  schemas/           # Pydantic request/response models
  services/
    tesla_client.py  # Tesla Fleet API wrapper (token refresh, Fernet encryption)
    trip_detector.py # Detects trip start/end from snapshot shift_state transitions
    sync_service.py  # Polls vehicle data, syncs charging history
    cost_calculator.py
  tasks/scheduler.py # APScheduler background jobs (5-min poll)
backend/alembic/     # Database migrations (run via entrypoint.sh on startup)

frontend/src/
  api/               # Axios API client methods
  components/        # Charts, layout, common UI
  hooks/             # useTrips, useCharges, useSettings
  pages/             # Dashboard, Trips, Charging, Comparison, Settings, Connect
  store/authStore.ts # Zustand auth state
  utils/formatters.ts
  App.tsx            # React Router config
frontend/nginx.conf  # Production nginx: serves SPA + proxies /api/ to backend, HTTPS
```

## Authentication — Token Paste (no developer account needed)

No Tesla developer registration required. Uses the same token approach as TeslaMate:

1. User visits [myteslamate.com/tesla-token](https://www.myteslamate.com/tesla-token) and logs in with Tesla
2. Copies the Access Token and Refresh Token
3. Pastes both into the Connect page (`/connect`) in the app
4. Backend calls `POST /api/auth/connect`, validates tokens against Tesla API, stores encrypted

Tokens auto-refresh in the background. If refresh token expires (~90 days unused), user re-pastes.

## Environment Setup

Copy `backend/.env.example` to `backend/.env`:

```
ENCRYPTION_KEY=    # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
DATABASE_URL=postgresql+asyncpg://tesla:tesla@db:5432/tesla_tracker
FRONTEND_URL=http://localhost:5173
```

No Tesla credentials needed in `.env`.

## Database (PostgreSQL, 5 tables)

Managed by Alembic — `entrypoint.sh` runs `alembic upgrade head` on every container start.

- **vehicles** — VIN, tokens (Fernet-encrypted), battery capacity
- **trips** — start/end odometer, kWh used, efficiency (mi/kWh), locations
- **charge_sessions** — kWh added, charger type, cost (home = kWh × rate; supercharger from Tesla billing)
- **vehicle_snapshots** — Raw 5-min poll data (shift_state, odometer, battery %, GPS)
- **settings** — electricity rate, gas price, comparison MPG, sync interval

## Deployment (NAS via GitHub Actions)

- `docker-compose.yml` — local dev (postgres + backend + frontend)
- `docker-compose.nas.yml` — NAS reference (pulls GHCR images, port 8090, Tailscale cert mounts)
- `.github/workflows/deploy.yml` — on push to main: builds both images → GHCR → SSH deploy to NAS via Tailscale

NAS deploy dir: `~/tesla-tracker/`. Requires `NAS_TAILSCALE_IP`, `NAS_USER`, `NAS_SSH_KEY`, `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_CLIENT_SECRET` as GitHub secrets.

## Key Architecture Notes

**Trip detection**: No native Tesla trip API. Backend polls `vehicle_data` every 5 minutes and watches `shift_state` transitions — P/null → D/R = trip start, D/R → P/null = trip end. Trips under 5 minutes may be missed.

**Charging sync**: Pulled from Tesla's `GET /api/1/dx/charging/history`. Home charging cost = kWh × electricity rate from settings. Supercharger cost comes from Tesla billing data.

**Token storage**: Access/refresh tokens stored encrypted (Fernet) in the `vehicles` table.

**Charger classification** by peak power: ≥50 kW = dc_fast, ≥7 kW = destination, <7 kW = home.

**nginx HTTPS**: Production container listens on 443 with Tailscale-provisioned cert mounted from `/var/lib/tailscale/certs/`. `TAILSCALE_HOSTNAME` must be set in NAS `.env`.

## Critical Constraint

**SQLAlchemy must be >=2.0.48** — older versions have a Union typing incompatibility with Python 3.14. Do not downgrade.

## API Routes Summary

```
POST /api/auth/connect        # Store pasted access + refresh tokens
GET  /api/auth/status         # {authenticated, vehicle_count}
DELETE /api/auth/logout       # Clear all tokens
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
