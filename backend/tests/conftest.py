"""
Shared test fixtures.

Environment setup happens at module level (before any app imports) so that
Pydantic Settings reads the correct values when the app is first imported.
"""

import os

# Generate a throw-away encryption key if one isn't already set.
# Must happen before importing anything from app.config.
if not os.environ.get("ENCRYPTION_KEY"):
    from cryptography.fernet import Fernet
    os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://tesla:tesla@localhost:5432/tesla_tracker_test",
)
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app

engine = create_async_engine(os.environ["DATABASE_URL"])
_session_factory = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Create all tables once per test session, drop them at the end."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(autouse=True)
async def clean_db():
    """Truncate every table before each test so tests are fully isolated."""
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield


@pytest.fixture
async def db_session() -> AsyncSession:
    async with _session_factory() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()
