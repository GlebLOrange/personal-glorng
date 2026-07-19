from unittest.mock import AsyncMock, patch

from httpx import AsyncClient


class TestFeedbackRateLimit:
    """Rate limit on POST /api/feedback is 5 requests per 300 seconds."""

    async def test_allows_within_limit(self, client: AsyncClient):
        with patch("app.routers.feedback.notify_admin", new_callable=AsyncMock):
            for _ in range(5):
                resp = await client.post(
                    "/api/feedback",
                    json={
                        "email": "test@example.com",
                        "theme": "Test",
                        "message": "Hello",
                    },
                )
                assert resp.status_code == 201

    async def test_blocks_over_limit(self, client: AsyncClient):
        with patch("app.routers.feedback.notify_admin", new_callable=AsyncMock):
            for _ in range(5):
                await client.post(
                    "/api/feedback",
                    json={
                        "email": "test@example.com",
                        "theme": "Test",
                        "message": "Hello",
                    },
                )

            resp = await client.post(
                "/api/feedback",
                json={
                    "email": "test@example.com",
                    "theme": "Test",
                    "message": "This one should be blocked",
                },
            )
            assert resp.status_code == 429
            assert "Too many requests" in resp.json()["detail"]
