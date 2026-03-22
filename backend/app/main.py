from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, charges, settings as settings_router, stats, trips, vehicles
from app.tasks.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler(interval_minutes=5)
    yield
    stop_scheduler()


app = FastAPI(title="Tesla Tracker", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(trips.router)
app.include_router(charges.router)
app.include_router(stats.router)
app.include_router(settings_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
