from httpx import AsyncClient, Cookies


def _set_cookie(client: AsyncClient, user_id: int):
    """Helper to set userId cookie on client."""
    cookies = Cookies()
    cookies.set("userId", str(user_id), domain="test")
    client.cookies = cookies


class TestAuthRegister:
    """Tests for auth registration endpoint."""

    async def test_register_success(self, client: AsyncClient):
        response = await client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["status"] == "pending"
        assert "message" in data

    async def test_register_short_username(self, client: AsyncClient):
        response = await client.post("/api/auth/register", json={
            "username": "ab",
            "email": "short@example.com",
            "password": "password123"
        })
        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        response = await client.post("/api/auth/register", json={
            "username": "validuser",
            "email": "short@example.com",
            "password": "short"
        })
        assert response.status_code == 422

    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        response = await client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "dup@example.com",
            "password": "password123"
        })
        assert response.status_code == 400


class TestAuthLogin:
    """Tests for auth login endpoint."""

    async def test_login_success(self, client: AsyncClient, test_user):
        response = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        response = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "password123"
        })
        assert response.status_code == 401

    async def test_login_pending_user(self, client: AsyncClient, test_user_pending):
        response = await client.post("/api/auth/login", json={
            "username": "pendinguser",
            "password": "testpass123"
        })
        assert response.status_code == 401


class TestAuthProfile:
    """Tests for auth profile endpoints."""

    async def test_get_me(self, client: AsyncClient, test_user):
        _set_cookie(client, test_user.id)
        response = await client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["status"] == "approved"

    async def test_get_me_unauthorized(self, client: AsyncClient):
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    async def test_update_profile(self, client: AsyncClient, test_user):
        _set_cookie(client, test_user.id)
        response = await client.put("/api/auth/profile", json={
            "email": "newemail@example.com"
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Profile updated"

    async def test_search_users(self, client: AsyncClient, test_user, another_user):
        _set_cookie(client, test_user.id)
        response = await client.get("/api/auth/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(u["username"] == "testuser" for u in data)
