
import pytest_asyncio

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
)

from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from httpx import AsyncClient, ASGITransport

from app.database.db import Base, get_session
from app.main import app


# -----------------------------------
# TEST DATABASE
# -----------------------------------

TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:yashwanth@localhost:5432/github_tracker_test"
)


# -----------------------------------
# TEST ENGINE
# -----------------------------------

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool
)


# -----------------------------------
# SESSION
# -----------------------------------

TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# -----------------------------------
# OVERRIDE SESSION
# -----------------------------------

async def override_get_session():

    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


# -----------------------------------
# CREATE TABLES
# -----------------------------------

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


# -----------------------------------
# CLEAN DATABASE
# -----------------------------------

@pytest_asyncio.fixture(autouse=True)
async def clean_db():

    async with engine.begin() as conn:

        await conn.execute(
            text(
                "TRUNCATE TABLE repositories RESTART IDENTITY CASCADE"
            )
        )

    yield


# -----------------------------------
# CLIENT
# -----------------------------------

@pytest_asyncio.fixture
async def client():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:

        yield ac

