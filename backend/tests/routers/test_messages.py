from httpx import AsyncClient, Cookies


def _set_cookie(client: AsyncClient, user_id: int):
    """Helper to set userId cookie on client."""
    cookies = Cookies()
    cookies.set("userId", str(user_id), domain="test")
    client.cookies = cookies


class TestMessages:
    """Tests for message endpoints."""

    async def test_send_message(self, client: AsyncClient, test_user, another_user):
        _set_cookie(client, test_user.id)
        create_resp = await client.post("/api/chats", json={
            "name": "Test Group",
            "member_ids": [another_user.id]
        })
        chat_id = create_resp.json()["id"]

        response = await client.post("/api/messages", json={
            "chat_id": chat_id,
            "content": "Hello, world!"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Hello, world!"
        assert data["chat_id"] == chat_id

    async def test_get_messages(self, client: AsyncClient, test_user, another_user):
        _set_cookie(client, test_user.id)
        create_resp = await client.post("/api/chats", json={
            "name": "Test Group",
            "member_ids": [another_user.id]
        })
        chat_id = create_resp.json()["id"]

        await client.post("/api/messages", json={
            "chat_id": chat_id,
            "content": "First message"
        })
        await client.post("/api/messages", json={
            "chat_id": chat_id,
            "content": "Second message"
        })

        response = await client.get(f"/api/messages/{chat_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["content"] == "First message"
        assert data[1]["content"] == "Second message"

    async def test_send_message_empty_content(self, client: AsyncClient, test_user):
        response = await client.post("/api/messages", json={
            "chat_id": 1,
            "content": ""
        })
        assert response.status_code == 422

    async def test_send_message_invalid_chat_id(self, client: AsyncClient, test_user):
        response = await client.post("/api/messages", json={
            "chat_id": -1,
            "content": "Hello"
        })
        assert response.status_code == 422


class TestLeaveChat:
    """Tests for leaving chats."""

    async def test_leave_chat(self, client: AsyncClient, test_user, another_user):
        _set_cookie(client, test_user.id)
        create_resp = await client.post("/api/chats", json={
            "name": "Test Group",
            "member_ids": [another_user.id]
        })
        chat_id = create_resp.json()["id"]

        response = await client.post(f"/api/chats/{chat_id}/leave")
        assert response.status_code == 200
        assert response.json()["message"] == "Left chat"
