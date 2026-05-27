import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_resume_has_required_fields(client: AsyncClient) -> None:
    resp = await client.get("/api/resume")
    assert resp.status_code == 200
    data = resp.json()
    assert "name" in data
    assert "title" in data
    assert "skills" in data
    assert "experience" in data
    assert "projects" in data
    assert "links" in data


@pytest.mark.asyncio
async def test_resume_skills_structure(client: AsyncClient) -> None:
    resp = await client.get("/api/resume")
    skills = resp.json()["skills"]
    assert isinstance(skills, list)
    assert len(skills) > 0
    for skill in skills:
        assert "category" in skill
        assert "items" in skill


@pytest.mark.asyncio
async def test_resume_name(client: AsyncClient) -> None:
    resp = await client.get("/api/resume")
    assert resp.status_code == 200
    assert resp.json()["name"] == "gLOrng"
