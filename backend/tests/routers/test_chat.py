from httpx import AsyncClient, Cookies


def _set_cookie(client: AsyncClient, user_id: int):
    """Helper to set userId cookie on client."""
    cookies = Cookies()
    cookies.set("userId", str(user_id), domain="test")
    client.cookies = cookies


class TestChatCreate:
    """Tests for chat creation endpoints."""

    async def test_create_group_chat(self, client: AsyncClient, test_user, another_user):
        _set_cookie(client, test_user.id)
        response = await client.post("/api/chats", json={
            "name": "Test Group",
            "member_ids": [another_user.id]
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Group"
        assert data["type"] == "group"

    async def test_create_direct_chat(self, client: AsyncClient, test_user, another_user):
        _set_cookie(client, test_user.id)
        response = await client.post("/api/chats/direct", json={
            "participant_id": another_user.id
        })
        assert response.status_code == 201
        data = response.json()
        assert "chat_id" in data

    async def test_get_chats(self, client: AsyncClient, test_user, another_user):
        _set_cookie(client, test_user.id)
        create_resp = await client.post("/api/chats", json={
            "name": "Test Group",
            "member_ids": [another_user.id]
        })
        assert create_resp.status_code == 201

        response = await client.get("/api/chats")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_chat_members(self, client: AsyncClient, test_user, another_user):
        _set_cookie(client, test_user.id)
        create_resp = await client.post("/api/chats", json={
            "name": "Test Group",
            "member_ids": [another_user.id]
        })
        chat_id = create_resp.json()["id"]

        response = await client.get(f"/api/chats/{chat_id}/members")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2


class TestChatMembers:
    """Tests for chat member management."""

    async def test_add_member(self, client: AsyncClient, test_user, another_user):
        _set_cookie(client, test_user.id)
        create_resp = await client.post("/api/chats", json={
            "name": "Test Group",
            "member_ids": []
        })
        chat_id = create_resp.json()["id"]

        response = await client.post(f"/api/chats/{chat_id}/members", json={
            "user_id": another_user.id
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Member added"

    async def test_remove_member(self, client: AsyncClient, test_user, another_user):
        _set_cookie(client, test_user.id)
        create_resp = await client.post("/api/chats", json={
            "name": "Test Group",
            "member_ids": [another_user.id]
        })
        chat_id = create_resp.json()["id"]

        response = await client.delete(f"/api/chats/{chat_id}/members/{another_user.id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Member removed"


class TestAdmin:
    """Tests for admin endpoints."""

    async def test_get_pending_users(self, client: AsyncClient, test_user, test_user_pending):
        _set_cookie(client, test_user.id)
        response = await client.get("/api/chats/admin/users")
        assert response.status_code == 200
        data = response.json()
        assert any(u["username"] == "pendinguser" for u in data)

    async def test_approve_user(self, client: AsyncClient, test_user, test_user_pending):
        _set_cookie(client, test_user.id)
        response = await client.put(f"/api/chats/admin/users/{test_user_pending.id}/approve")
        assert response.status_code == 200
        assert response.json()["message"] == "User approved"

    async def test_block_user(self, client: AsyncClient, test_user, test_user_pending):
        _set_cookie(client, test_user.id)
        response = await client.put(f"/api/chats/admin/users/{test_user_pending.id}/block")
        assert response.status_code == 200
        assert response.json()["message"] == "User blocked"
