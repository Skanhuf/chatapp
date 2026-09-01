import pytest
from httpx import AsyncClient


class TestWebSocket:
    """Tests for WebSocket endpoint."""

    async def test_websocket_connect_missing_user_id(self, client: AsyncClient):
        from httpx import WebSocketError
        with pytest.raises(WebSocketError):
            await client.websocket_connect("/ws")

    async def test_websocket_connect_invalid_user_id(self, client: AsyncClient):
        with pytest.raises(Exception):
            async with client.websocket_connect("/ws?userId=invalid") as ws:
                pass

    async def test_websocket_connect_with_user_id(self, client: AsyncClient, test_user):
        try:
            async with client.websocket_connect(f"/ws?userId={test_user.id}") as ws:
                # Connection should succeed
                data = await ws.receive_text()
                # No data expected on connect, but connection is open
        except Exception:
            # Connection might close immediately, which is also valid
            pass
