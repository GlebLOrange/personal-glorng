import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sitemap_xml(client: AsyncClient) -> None:
    resp = await client.get("/sitemap.xml")
    assert resp.status_code == 200
    assert "application/xml" in resp.headers["content-type"]
    body = resp.text
    assert "<loc>http://localhost/</loc>" in body
    assert "<loc>http://localhost/privacy</loc>" in body
    assert "<loc>http://localhost/tools</loc>" in body
    assert "<loc>http://localhost/news</loc>" in body
    assert "<loc>http://localhost/calculator</loc>" not in body
    assert "<loc>http://localhost/weather</loc>" not in body
    assert "/admin" not in body


@pytest.mark.asyncio
async def test_robots_txt(client: AsyncClient) -> None:
    resp = await client.get("/robots.txt")
    assert resp.status_code == 200
    body = resp.text
    assert "Disallow: /admin" in body
    assert "Disallow: /login" in body
    assert "Disallow: /settings" in body
    assert "Sitemap: http://localhost/sitemap.xml" in body
