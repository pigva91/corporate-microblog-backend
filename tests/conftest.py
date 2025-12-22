import os
import tempfile
from typing import Any, AsyncGenerator
from unittest.mock import patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database import Base
from app.deps import get_db
from app.main import app
from app.models import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSession = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
def mock_settings():
    test_settings = {
        "postgres_user": "test_user",
        "postgres_password": "test_password",
        "postgres_host": "localhost",
        "postgres_port": "5432",
        "postgres_db": "test_db",
        "media_folder": "/media"
    }

    with patch("app.config.settings", **test_settings):
        yield


@pytest_asyncio.fixture
async def db_session(prepare_database) -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSession() as session:
        yield session


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSession() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def prepare_database() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
def temp_media_folder():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["media_folder"] = tmpdir
        os.makedirs(tmpdir, exist_ok=True)
        yield


@pytest_asyncio.fixture
async def async_client(
    prepare_database, temp_media_folder
) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(prepare_database) -> AsyncGenerator[User, None]:
    async with TestAsyncSession() as db:
        user = User(name="Ivan", api_key="ivan_key")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        yield user


@pytest_asyncio.fixture
async def another_user(prepare_database) -> AsyncGenerator[User, None]:
    async with TestAsyncSession() as db:
        user = User(name="Boris", api_key="boris_key")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        yield user


@pytest_asyncio.fixture
async def test_user_id(prepare_database) -> AsyncGenerator[int, None]:
    async with TestAsyncSession() as db:
        user = User(name="Ivan", api_key="ivan_key")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        yield user.id


@pytest_asyncio.fixture
async def another_user_id(prepare_database) -> AsyncGenerator[int, None]:
    async with TestAsyncSession() as db:
        user = User(name="Boris", api_key="boris_key")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        yield user.id
