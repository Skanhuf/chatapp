import pytest


class TestAuthService:
    """Tests for auth service layer."""

    async def test_register_success(self, session):
        import bcrypt

        from repositories.user_repo import UserRepository
        from services.auth_service import AuthService

        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo)

        user = await auth_service.register("newuser", "new@example.com", "password123")
        assert user.username == "newuser"
        assert user.status == "pending"

        # Verify password is hashed
        assert user.password_hash != "password123"
        assert bcrypt.checkpw(b"password123", user.password_hash.encode("utf-8"))

    async def test_register_short_username(self, session):
        from repositories.user_repo import UserRepository
        from services.auth_service import AuthService

        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo)

        with pytest.raises(ValueError, match="username must be at least 3"):
            await auth_service.register("ab", "test@example.com", "password123")

    async def test_register_duplicate_username(self, session, test_user):
        from repositories.user_repo import UserRepository
        from services.auth_service import AuthService

        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo)

        with pytest.raises(ValueError, match="username already taken"):
            await auth_service.register("testuser", "other@example.com", "password123")

    async def test_login_success(self, session, test_user):
        from repositories.user_repo import UserRepository
        from services.auth_service import AuthService

        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo)

        user = await auth_service.login("testuser", "testpass123")
        assert user.username == "testuser"

    async def test_login_wrong_password(self, session, test_user):
        from repositories.user_repo import UserRepository
        from services.auth_service import AuthService

        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo)

        with pytest.raises(ValueError, match="invalid credentials"):
            await auth_service.login("testuser", "wrongpassword")

    async def test_login_pending_user(self, session, test_user_pending):
        from repositories.user_repo import UserRepository
        from services.auth_service import AuthService

        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo)

        with pytest.raises(ValueError, match="account not approved"):
            await auth_service.login("pendinguser", "testpass123")

    async def test_search_users(self, session, test_user, another_user):
        from repositories.user_repo import UserRepository
        from services.auth_service import AuthService

        user_repo = UserRepository(session)
        auth_service = AuthService(user_repo)

        users = await auth_service.search_users("test")
        assert len(users) >= 1
        assert any(u.username == "testuser" for u in users)
