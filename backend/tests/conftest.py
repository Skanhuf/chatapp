import pytest
import pytest_asyncio
import asyncio
import tempfile
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from main import app
from database.db import Base, get_db


TEST_DB_PATH = tempfile.mktemp(suffix=".db")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
_test_session = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Create tables on the engine's connection before any tests run."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session():
    """
    Use the same engine as setup_db.
    The key: connect first, THEN create tables on this connection,
    THEN start the transaction.
    """
    async with _engine.connect() as conn:
        # Create tables on THIS connection before starting transaction
        await conn.run_sync(Base.metadata.create_all)
        txn = await conn.begin()
        s = _test_session(bind=conn)
        try:
            yield s
        finally:
            await s.close()
            await txn.rollback()


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
