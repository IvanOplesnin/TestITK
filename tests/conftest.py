import asyncio

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.db import get_session
from backend.models import Base
from backend import app as real_app
from backend.models.wallet import Wallet


@pytest_asyncio.fixture(loop_scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="module")
async def async_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine):
    session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="module")
async def with_data_session(async_engine):
    session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session() as session:
        async with session.begin():
            await session.execute(
                insert(Wallet).values([
                    {"uuid": "00000000-0000-0000-0000-000000000001", "balance": 100},
                    {"uuid": "00000000-0000-0000-0000-000000000002", "balance": 50},
                ])
            )

        yield session
        await session.rollback()


@pytest.fixture
def app(with_data_session) -> FastAPI:
    real_app.dependency_overrides[get_session] = lambda: with_data_session
    return real_app


@pytest.fixture
async def client(app):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
