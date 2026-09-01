import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from main import app
from database.db import Base, get_db


# PostgreSQL test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/chatapp_test"

_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
_test_session = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Create tables once for the entire test session."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session():
    """Provide a session with rollback."""
    async with _engine.connect() as conn:
        await conn.begin()
        s = _test_session(bind=conn)
        try:
            yield s
        finally:
            await s.close()


@pytest_asyncio.fixture
async def client(session):
    """Provide an HTTP test client."""
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(session):
    import bcrypt
    from models.models import User

    password_hash = bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode("utf-8")
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=password_hash,
        status="approved",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_pending(session):
    import bcrypt
    from models.models import User

    password_hash = bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode("utf-8")
    user = User(
        username="pendinguser",
        email="pending@example.com",
        password_hash=password_hash,
        status="pending",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def another_user(session):
    import bcrypt
    from models.models import User

    password_hash = bcrypt.hashpw(b"anotherpass123", bcrypt.gensalt()).decode("utf-8")
    user = User(
        username="anotheruser",
        email="another@example.com",
        password_hash=password_hash,
        status="approved",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
