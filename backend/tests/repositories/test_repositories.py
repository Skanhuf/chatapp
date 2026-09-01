import pytest


class TestUserRepository:
    """Tests for user repository."""

    async def test_create_user(self, session):
        from repositories.user_repo import UserRepository
        from models.models import User
        import bcrypt

        user_repo = UserRepository(session)
        password_hash = bcrypt.hashpw(b"testpass", bcrypt.gensalt()).decode("utf-8")

        user = User(
            id=0, username="repo_user", email="repo@test.com",
            password_hash=password_hash, status="approved", created_at=None
        )
        created = await user_repo.create(user)
        assert created.id > 0
        assert created.username == "repo_user"

    async def test_find_by_username(self, session, test_user):
        from repositories.user_repo import UserRepository

        user_repo = UserRepository(session)
        user = await user_repo.find_by_username("testuser")
        assert user is not None
        assert user.username == "testuser"

    async def test_find_by_id(self, session, test_user):
        from repositories.user_repo import UserRepository

        user_repo = UserRepository(session)
        user = await user_repo.find_by_id(test_user.id)
        assert user is not None
        assert user.id == test_user.id

    async def test_get_pending(self, session, test_user_pending):
        from repositories.user_repo import UserRepository

        user_repo = UserRepository(session)
        pending = await user_repo.get_pending()
        assert any(u.username == "pendinguser" for u in pending)

    async def test_approve_user(self, session, test_user_pending):
        from repositories.user_repo import UserRepository

        user_repo = UserRepository(session)
        await user_repo.approve(test_user_pending.id)

        user = await user_repo.find_by_id(test_user_pending.id)
        assert user.status == "approved"

    async def test_block_user(self, session, test_user_pending):
        from repositories.user_repo import UserRepository

        user_repo = UserRepository(session)
        await user_repo.block(test_user_pending.id)

        user = await user_repo.find_by_id(test_user_pending.id)
        assert user.status == "blocked"


class TestChatRepository:
    """Tests for chat repository."""

    async def test_create_chat(self, session, test_user):
        from repositories.chat_repo import ChatRepository
        from models.models import Chat

        chat_repo = ChatRepository(session)
        chat = Chat(
            id=0, name="Test Chat", chat_type="group",
            created_by=test_user.id, created_at=None
        )
        created = await chat_repo.create(chat)
        assert created.id > 0
        assert created.name == "Test Chat"

    async def test_create_direct_chat(self, session, test_user, another_user):
        from repositories.chat_repo import ChatRepository

        chat_repo = ChatRepository(session)
        chat_id = await chat_repo.create_direct_chat(test_user.id, another_user.id)
        assert chat_id > 0


class TestMessageRepository:
    """Tests for message repository."""

    async def test_save_message(self, session, test_user):
        from repositories.message_repo import MessageRepository
        from models.models import Message

        message_repo = MessageRepository(session)
        msg = Message(
            id=0, chat_id=1, user_id=test_user.id,
            content="Test message", file_url=None,
            created_at=None, username=None
        )
        saved = await message_repo.save(msg)
        assert saved.id > 0
        assert saved.content == "Test message"
