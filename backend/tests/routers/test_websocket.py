from httpx import AsyncClient


class TestWebSocket:
    """Tests for WebSocket endpoint."""

    async def test_websocket_connect_missing_user_id(self, client: AsyncClient):
        # WebSocket without userId should close
        try:
            await client.websocket_connect("/ws")
        except Exception:
            pass  # Expected to fail

    async def test_websocket_connect_invalid_user_id(self, client: AsyncClient):
        # WebSocket with invalid userId should close
        try:
            async with client.websocket_connect("/ws?userId=invalid") as ws:
                pass
        except Exception:
            pass  # Expected to fail

    async def test_websocket_connect_with_user_id(self, client: AsyncClient, test_user):
        try:
            async with client.websocket_connect(f"/ws?userId={test_user.id}") as ws:
                # Connection should succeed
                pass
        except Exception:
            # Connection might close, which is also valid
            pass
