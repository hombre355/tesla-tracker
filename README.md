# Tesla Tracker

Track your Tesla Model 3 energy usage, charging costs, and see how much you save compared to a gas car. Runs privately on your home NAS — no cloud accounts or subscriptions required.

## Features

- **Trip tracking** — energy used per trip, miles driven, efficiency (mi/kWh)
- **Charging history** — kWh added, cost per session, home vs Supercharger breakdown
- **Gas car comparison** — monthly electricity cost vs equivalent gas vehicle cost, cumulative savings
- **Charts & trends** — efficiency over time, charging cost trends, monthly comparison

## Tech Stack

- **Backend**: Python / FastAPI / PostgreSQL / SQLAlchemy async / Alembic / APScheduler
- **Frontend**: React 18 / Vite / TypeScript / Tailwind CSS / Recharts
- **Deployment**: Docker Compose + GitHub Actions → NAS via Tailscale SSH

---

## Local Development

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — generate ENCRYPTION_KEY:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173).

### 3. Run tests

Requires a PostgreSQL instance (can reuse the Docker one):

```bash
# Start just the DB
docker compose up -d db

# Run tests
DATABASE_URL=postgresql+asyncpg://tesla:tesla@localhost:5432/tesla_tracker_test \
PYTHONPATH=backend \
pip install -r backend/requirements-test.txt && \
pytest backend/tests/ -v
```

Tests run automatically in CI on every push to `main`. A failure blocks the build and deploy.

### 4. Full stack with Docker

```bash
docker compose up --build
```

---

## Connect Your Tesla

No Tesla developer account required. Uses the same token approach as TeslaMate:

1. Visit **[myteslamate.com/tesla-token](https://www.myteslamate.com/tesla-token)** and log in with your Tesla account
2. Copy the **Access Token** and **Refresh Token**
3. Open the app → **Connect** page → paste both tokens → click Connect

The app validates the tokens, discovers your vehicle, and starts polling every 5 minutes. Tokens refresh automatically. If they ever expire (~90 days unused), just repeat the steps above.

---

## How Trip Detection Works

Tesla's Fleet API has no trip history endpoint. Trips are reconstructed by:

1. Polling `vehicle_data` every 5 minutes (configurable in Settings)
2. Watching `shift_state`: `P/null → D/R` = trip start, `D/R → P/null` = trip end
3. Computing energy used: `(start_battery_pct - end_battery_pct) / 100 × pack_capacity_kWh`

**Note**: Short trips under ~5 minutes may be missed if the poll happens after the trip ends.

## How Charging Works

Charging sessions are pulled from Tesla's charging history API:
- Supercharger sessions include cost from Tesla's billing
- Home charging cost = `kWh added × your electricity rate` (set in Settings)

Click **Sync Now** on the Charging page to pull the latest history immediately.

---

## NAS Deployment

The app deploys automatically on every push to `main` via GitHub Actions:

1. Builds `backend` and `frontend` Docker images in parallel
2. Pushes both to GitHub Container Registry (GHCR)
3. Connects to the NAS via Tailscale SSH and runs `docker compose pull && up -d`

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `NAS_TAILSCALE_IP` | NAS Tailscale IP (100.x.x.x) |
| `NAS_USER` | NAS SSH username |
| `NAS_SSH_KEY` | NAS private SSH key |
| `TS_OAUTH_CLIENT_ID` | Tailscale OAuth client ID (for CI access) |
| `TS_OAUTH_CLIENT_SECRET` | Tailscale OAuth client secret |

### NAS One-Time Setup

SSH into the NAS and create `~/tesla-tracker/.env`:

```
ENCRYPTION_KEY=your_fernet_key
DATABASE_URL=postgresql+asyncpg://tesla:tesla@db:5432/tesla_tracker
FRONTEND_URL=http://your-nas-ip:8090
TAILSCALE_HOSTNAME=your-nas-name.tail12345.ts.net
```

Generate `ENCRYPTION_KEY`:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Provision the Tailscale HTTPS cert:
```bash
sudo tailscale cert your-nas-name.tail12345.ts.net
sudo chmod 644 /var/lib/tailscale/certs/*.crt
sudo chmod 640 /var/lib/tailscale/certs/*.key
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ENCRYPTION_KEY` | Fernet key for encrypting stored Tesla tokens |
| `DATABASE_URL` | PostgreSQL connection string |
| `FRONTEND_URL` | Frontend base URL (used for CORS) |
| `TAILSCALE_HOSTNAME` | NAS Tailscale hostname (for cert volume mount, NAS only) |
