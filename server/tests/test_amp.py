import re
from urllib.parse import urlparse

from httpx import AsyncClient

_SCRIPT_SRC_RE = re.compile(
    r'<script[^>]*\ssrc=["\']([^"\']+)["\']',
    re.IGNORECASE,
)


class TestAmpPage:
    async def test_amp_returns_html(self, client: AsyncClient):
        resp = await client.get("/amp")
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")
        body = resp.text
        assert "<html" in body
        assert "⚡" in body
        script_hosts = [urlparse(src).hostname for src in _SCRIPT_SRC_RE.findall(body)]
        assert "cdn.ampproject.org" in script_hosts
        assert "Gleb.Y" in body
        assert "Backend-heavy full-stack" in body
        assert 'rel="canonical"' in body
