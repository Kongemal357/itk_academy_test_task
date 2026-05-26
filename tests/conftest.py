import asyncio
import os
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.db.database import Base, get_session
from src.main import app

DATABASE_URL_TEST = os.getenv("DATABASE_URL_TEST")

# ==================== INTEGRATION DB ====================

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        DATABASE_URL_TEST,
        poolclass=NullPool,
        connect_args={"timeout": 10, "command_timeout": 10},
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function", autouse=True)
async def prepare_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="function")
async def db_session(engine):
    async with engine.connect() as connection:
        async_session = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        session = async_session()
        yield session
        await session.rollback()
        await session.close()


# ==================== UNIT DB ====================

@pytest.fixture
def mock_session():
    """Mock DB session for unit tests."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def sample_wallet_uuid():
    """Fixed UUID for reproducible unit tests."""
    return uuid.UUID("550e8400-e29b-41d4-a716-446655440000")


@pytest.fixture
def sample_wallet(sample_wallet_uuid):
    """Mock wallet object for unit tests."""
    wallet = MagicMock()
    wallet.uuid = sample_wallet_uuid
    wallet.balance = Decimal("1000.00")
    wallet.id = 1
    return wallet


# ==================== CLIENT ====================
@pytest.fixture
async def integration_client(engine):
    """Client with real test DB — each request gets its own session."""

    async def override_get_session():
        async with engine.connect() as connection:
            async_session = async_sessionmaker(
                bind=connection,
                expire_on_commit=False,
                class_=AsyncSession,
            )
            session = async_session()
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test", timeout=30.0
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def unit_client(mock_session):
    """Client with mocked DB."""
    async def override_get_session():
        yield mock_session
    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
