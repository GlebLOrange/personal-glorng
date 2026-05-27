from httpx import AsyncClient


class TestAmpPage:
    async def test_amp_returns_html(self, client: AsyncClient):
        resp = await client.get("/amp")
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")
        body = resp.text
        assert "<html" in body and "⚡" in body
        assert "cdn.ampproject.org" in body
        assert "gLOrng" in body
        assert 'rel="canonical"' in body
