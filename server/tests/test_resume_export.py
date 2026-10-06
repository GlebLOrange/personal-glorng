"""Tests for resume export endpoints and selection helpers."""

from __future__ import annotations

import json

import pytest
from httpx import AsyncClient

from app.content.resume_data import RESUME_DATA, RESUME_DOCUMENT
from app.schemas.resume import ResumeDocument
from app.services.resume_export import (
    build_recruiter_profile,
    build_share_query,
    render_resume_markdown,
    resume_json_bytes,
    select_resume,
    skill_id,
)
from app.services.resume_pdf import render_resume_html


def test_resume_document_validates_canonical_data() -> None:
    """Canonical RESUME_DATA validates against ResumeDocument."""
    doc = ResumeDocument.model_validate(RESUME_DATA)
    assert doc.name == "Gleb.Y"
    assert doc.projects[0].slug == "cookie-auth-csrf"
    assert doc.certifications == []
    assert doc.languages == []


def test_skill_id_derivation() -> None:
    """Skill ids are lowercase hyphenated labels without parentheses."""
    assert skill_id("Python") == "python"
    assert skill_id("Vue 3") == "vue-3"
    assert skill_id("CI/CD (GitHub Actions)") == "ci-cd"


def test_resume_json_round_trip() -> None:
    """JSON export round-trips through the canonical schema."""
    raw = resume_json_bytes(RESUME_DOCUMENT)
    payload = json.loads(raw.decode("utf-8"))
    doc = ResumeDocument.model_validate(payload)
    assert doc.model_dump(mode="json") == RESUME_DOCUMENT.model_dump(mode="json")


def test_resume_markdown_sections() -> None:
    """Markdown contains populated sections and omits empty education."""
    markdown = render_resume_markdown(RESUME_DOCUMENT)
    assert "## Summary" in markdown
    assert "## Skills" in markdown
    assert "## Experience" in markdown
    assert "## Projects" in markdown
    assert "## Links" in markdown
    assert "## Education" not in markdown
    assert "Python" in markdown
    assert "cookie auth & CSRF" in markdown


def test_recruiter_profile_copy() -> None:
    """Recruiter profile is a short paragraph naming stack and projects."""
    text = build_recruiter_profile(RESUME_DOCUMENT)
    sentences = [part for part in text.split(". ") if part.strip()]
    assert 3 <= len(sentences) <= 5
    assert "Python" in text
    assert "FastAPI" in text
    assert "cookie auth" in text.lower() or "SSRF" in text


def test_select_resume_filters_skills_and_projects() -> None:
    """Skill and project filters keep only matching entries."""
    selection = select_resume(
        skills="python,fastapi,not-a-skill",
        projects="cookie-auth-csrf,missing-project",
    )
    skill_labels = [item for group in selection.resume.skills for item in group.items]
    assert skill_labels == ["Python", "FastAPI"]
    assert [project.slug for project in selection.resume.projects] == ["cookie-auth-csrf"]
    assert selection.ignored_skills == ["not-a-skill"]
    assert selection.ignored_projects == ["missing-project"]


def test_select_resume_unknown_only_falls_back() -> None:
    """When every skill id is unknown, skills fall back to the full list."""
    selection = select_resume(skills="nope,also-nope")
    assert len(selection.resume.skills) == len(RESUME_DOCUMENT.skills)
    assert selection.ignored_skills == ["also-nope", "nope"]


def test_select_resume_empty_query_is_full() -> None:
    """Blank selection returns the full canonical resume."""
    selection = select_resume()
    assert selection.resume.model_dump() == RESUME_DOCUMENT.model_dump()
    assert selection.ignored_skills == []


def test_select_resume_sections_allowlist() -> None:
    """Section allowlist keeps identity and empties omitted sections."""
    selection = select_resume(sections="skills,projects")
    assert selection.resume.name == RESUME_DOCUMENT.name
    assert selection.resume.title == RESUME_DOCUMENT.title
    assert selection.resume.bio == ""
    assert selection.resume.experience == []
    assert selection.resume.skills
    assert selection.resume.projects


def test_build_share_query_is_deterministic() -> None:
    """Share query sorts values and uses a fixed parameter order."""
    assert (
        build_share_query(
            projects=["ssrf-safe-fetch", "cookie-auth-csrf"],
            skills=["fastapi", "python"],
            sections=["projects", "skills"],
        )
        == "sections=projects,skills&skills=fastapi,python&projects=cookie-auth-csrf,ssrf-safe-fetch"
    )


def test_render_resume_html_has_selectable_text() -> None:
    """PDF HTML source includes name and a project title as plain text."""
    html = render_resume_html(dict(RESUME_DATA))
    assert "Gleb.Y" in html
    assert "cookie auth &amp; CSRF" in html
    assert "size: A4" in html


@pytest.mark.asyncio
async def test_resume_markdown_download(client: AsyncClient) -> None:
    """Markdown endpoint returns a downloadable Markdown attachment."""
    resp = await client.get("/api/resume/markdown")
    assert resp.status_code == 200
    assert "text/markdown" in resp.headers["content-type"]
    assert "gleb.y.cv.md" in resp.headers["content-disposition"]
    assert "## Skills" in resp.text


@pytest.mark.asyncio
async def test_resume_json_download(client: AsyncClient) -> None:
    """JSON endpoint returns a downloadable JSON attachment."""
    resp = await client.get("/api/resume/json")
    assert resp.status_code == 200
    assert "application/json" in resp.headers["content-type"]
    assert "gleb.y.cv.json" in resp.headers["content-disposition"]
    payload = resp.json()
    assert payload["name"] == "Gleb.Y"
    assert payload["projects"][0]["slug"] == "cookie-auth-csrf"


@pytest.mark.asyncio
async def test_recruiter_profile_endpoint(client: AsyncClient) -> None:
    """Recruiter profile endpoint returns plain text."""
    resp = await client.get("/api/resume/recruiter-profile")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers["content-type"]
    assert "Python" in resp.text
    assert "FastAPI" in resp.text


@pytest.mark.asyncio
async def test_resume_profile_endpoint(client: AsyncClient) -> None:
    """Filtered profile endpoint returns resume plus ignored ids."""
    resp = await client.get(
        "/api/resume/profile",
        params={"skills": "python,fastapi,nope", "projects": "cookie-auth-csrf"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ignored_skills"] == ["nope"]
    skills = [item for group in data["resume"]["skills"] for item in group["items"]]
    assert skills == ["Python", "FastAPI"]
    assert [project["slug"] for project in data["resume"]["projects"]] == [
        "cookie-auth-csrf",
    ]
