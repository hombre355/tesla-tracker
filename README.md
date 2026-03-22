# Tesla Tracker

Track your Tesla Model 3 energy usage, charging costs, and see how much you save compared to a gas car.

## Features

- **Trip tracking** — energy used per trip, miles driven, efficiency (mi/kWh)
- **Charging history** — kWh added, cost per session, home vs Supercharger breakdown
- **Gas car comparison** — monthly electricity cost vs equivalent gas vehicle cost, cumulative savings
- **Charts & trends** — efficiency over time, charging cost trends, monthly comparison

## Tech Stack

- **Backend**: Python / FastAPI / SQLite (SQLAlchemy async) / APScheduler
- **Frontend**: React 18 / Vite / TypeScript / Tailwind CSS / Recharts

---

## Setup

### 1. Tesla Developer Registration (one-time)

1. Go to [developer.tesla.com](https://developer.tesla.com) and sign in with your Tesla account.
2. Create a new application. Set:
   - **Redirect URI**: `http://localhost:8000/api/auth/callback`
   - **Allowed Origin**: `http://localhost:5173`
3. Save your `CLIENT_ID` and `CLIENT_SECRET`.

4. Generate an EC key pair (Tesla requires P-256 / secp256r1):
   ```bash
   openssl ecparam -name prime256v1 -genkey -noout -out private.pem
   openssl ec -in private.pem -pubout -out public.pem
   ```

5. Replace the placeholder at `frontend/public/.well-known/appspecific/com.tesla.3p.public-key.pem` with the contents of `public.pem`.

6. Register your domain with Tesla (for local dev, use `localhost`):
   ```bash
   # First get a partner token, then:
   curl --request POST \
     --url 'https://fleet-api.prd.na.vn.cloud.tesla.com/api/1/partner_accounts' \
     --header 'Authorization: Bearer <PARTNER_TOKEN>' \
     --header 'Content-Type: application/json' \
     --data '{"domain": "localhost"}'
   ```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Tesla CLIENT_ID, CLIENT_SECRET, and generate an ENCRYPTION_KEY:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Start the backend
uvicorn app.main:app --reload --port 8000
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see the API documentation.

### 3. Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173).

### 4. Connect Your Tesla

1. Click **"Connect Tesla Account"** in the navbar (or visit `/connect`).
2. You'll be redirected to Tesla's login page.
3. Log in and approve the requested permissions.
4. You'll be redirected back to the dashboard.
5. The app will start polling your vehicle every 5 minutes.

---

## How Trip Detection Works

Tesla's Fleet API does not provide a trip history endpoint. Trips are reconstructed by:

1. Polling `vehicle_data` every 5 minutes (configurable in Settings).
2. Watching the `shift_state` field: `P/null → D/R` = trip start, `D/R → P/null` = trip end.
3. Computing energy used: `(start_battery_pct - end_battery_pct) / 100 × pack_capacity_kWh`

**Note**: The car must be awake and not in sleep mode for polling to work. Short trips under 5 minutes may be missed if the poll happens after the trip ends.

## How Charging Works

Charging sessions are pulled from Tesla's charging history API (`/api/1/dx/charging/history`):
- Supercharger sessions include cost from Tesla's billing.
- Home charging cost = `kWh added × your electricity rate` (set in Settings).

Click **"Sync Now"** in the Charging page or Settings to pull the latest history immediately.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TESLA_CLIENT_ID` | Your Tesla app client ID |
| `TESLA_CLIENT_SECRET` | Your Tesla app client secret |
| `TESLA_REDIRECT_URI` | OAuth callback URL |
| `TESLA_AUDIENCE` | Tesla Fleet API base URL |
| `ENCRYPTION_KEY` | Fernet key for encrypting stored tokens |
| `DATABASE_URL` | SQLite connection string |
| `FRONTEND_URL` | Frontend base URL for post-auth redirect |
