import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.db import Base, get_db
from main import app

# Use SQLite for tests (fast, no external dependencies)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Create tables once for the entire test session."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def session():
    """Provide a session with rollback (per-test, new connection)."""
    async with _test_engine.connect() as conn, conn.begin():
        s = async_sessionmaker(conn, class_=AsyncSession, expire_on_commit=False)()
        try:
            yield s
        finally:
            await s.close()


@pytest_asyncio.fixture(scope="function")
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


@pytest_asyncio.fixture(scope="function")
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


@pytest_asyncio.fixture(scope="function")
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


@pytest_asyncio.fixture(scope="function")
async def client(session, test_user):
    """Provide an HTTP test client."""
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
