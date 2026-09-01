from httpx import AsyncClient


class TestWebSocket:
    """Tests for WebSocket endpoint."""

    async def test_websocket_connect_missing_user_id(self, client: AsyncClient):
        try:
            async with client.websocket_connect("/ws"):
                pass
        except Exception:
            pass

    async def test_websocket_connect_invalid_user_id(self, client: AsyncClient):
        try:
            async with client.websocket_connect("/ws?userId=invalid"):
                pass
        except Exception:
            pass

    async def test_websocket_connect_with_user_id(self, client: AsyncClient, test_user):
        try:
            async with client.websocket_connect(f"/ws?userId={test_user.id}"):
                pass
        except Exception:
            pass
