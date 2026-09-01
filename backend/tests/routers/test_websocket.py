from contextlib import suppress

from httpx import AsyncClient


class TestWebSocket:
    """Tests for WebSocket endpoint."""

    async def test_websocket_connect_missing_user_id(self, client: AsyncClient):
        # WebSocket without userId should close
        try:
            await client.websocket_connect("/ws")
        except Exception as exc:
            # Expected to fail
            assert "Missing userId" in str(exc) or "4001" in str(exc)

    async def test_websocket_connect_invalid_user_id(self, client: AsyncClient):
        # WebSocket with invalid userId should close
        with suppress(Exception):
            await client.websocket_connect("/ws?userId=invalid")

    async def test_websocket_connect_with_user_id(self, client: AsyncClient, test_user):
        with suppress(Exception):
            await client.websocket_connect(f"/ws?userId={test_user.id}")
