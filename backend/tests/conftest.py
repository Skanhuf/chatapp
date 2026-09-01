import pytest
import pytest_asyncio
import asyncio
import tempfile
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from main import app
from database.db import Base, get_db


# Use a temp SQLite file for testing
TEST_DB_PATH = tempfile.mktemp(suffix=".db")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Create test database and tables."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session():
    """Create a test database session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as s:
        yield s
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session):
    """Create a test HTTP client."""
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(session):
    """Create a test user and return it."""
    from models.models import User
    import bcrypt

    password_hash = bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode("utf-8")
    user = User(
        id=0,
        username="testuser",
        email="test@example.com",
        password_hash=password_hash,
        status="approved",
        created_at=None
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_pending(session):
    """Create a pending test user."""
    from models.models import User
    import bcrypt

    password_hash = bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode("utf-8")
    user = User(
        id=0,
        username="pendinguser",
        email="pending@example.com",
        password_hash=password_hash,
        status="pending",
        created_at=None
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def another_user(session):
    """Create another test user."""
    from models.models import User
    import bcrypt

    password_hash = bcrypt.hashpw(b"anotherpass123", bcrypt.gensalt()).decode("utf-8")
    user = User(
        id=0,
        username="anotheruser",
        email="another@example.com",
        password_hash=password_hash,
        status="approved",
        created_at=None
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
