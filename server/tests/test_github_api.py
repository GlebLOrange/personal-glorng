"""Tests for GitHub repo/issue API endpoints."""

import pytest
from httpx import AsyncClient

from app.core.fernet_secrets import encrypt_secret
from app.db.documents.credential import GitHubCredential
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.schemas.github import GitHubRepoResponse
from app.settings import get_settings
from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file


@pytest.fixture(autouse=True)
def github_public_env(monkeypatch: pytest.MonkeyPatch) -> None:
    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "github-public.env")


def _sample_repo() -> GitHubRepoResponse:
    return GitHubRepoResponse(
        name="Hello-World",
        full_name="octocat/Hello-World",
        html_url="https://github.com/octocat/Hello-World",
        description="My first repo",
        language="Python",
        stargazers_count=100,
        fork=False,
        private=False,
        updated_at="2026-01-01T00:00:00Z",
    )


@pytest.mark.asyncio
async def test_public_github_repos(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_get_public_github_repos(*args: object, **kwargs: object):
        return "octocat", [_sample_repo()]

    monkeypatch.setattr(
        "app.routers.github_public.get_public_github_repos",
        fake_get_public_github_repos,
    )

    resp = await client.get("/api/github/repos")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "octocat/Hello-World"


@pytest.mark.asyncio
async def test_resume_includes_github_section(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_get_public_github_repos(*args: object, **kwargs: object):
        return "octocat", [_sample_repo()]

    monkeypatch.setattr(
        "app.routers.resume.get_public_github_repos",
        fake_get_public_github_repos,
    )

    resp = await client.get("/api/resume")
    assert resp.status_code == 200
    github = resp.json()["github"]
    assert github["enabled"] is True
    assert github["username"] == "octocat"
    assert len(github["repos"]) == 1


@pytest.mark.asyncio
async def test_auth_github_status_returns_503_when_credentials_unavailable(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    original = registry.credentials
    registry.credentials = None
    try:
        resp = await auth_client.get("/api/auth/github/status")
        assert resp.status_code == 503
        assert resp.json()["detail"] == "Credential store unavailable"
    finally:
        registry.credentials = original


@pytest.mark.asyncio
async def test_auth_github_repos_requires_link(auth_client: AsyncClient) -> None:
    resp = await auth_client.get("/api/auth/github/repos")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_github_repos_with_token(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
    admin_user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    encrypted = encrypt_secret("gh-token", get_settings().JWT_SECRET)
    assert registry.credentials is not None
    await registry.credentials.upsert_github(
        GitHubCredential(
            user_id=admin_user.id,
            github_user_id=1,
            github_username="octocat",
            access_token=encrypted,
        ),
    )

    async def fake_list_user_repos(access_token: str) -> list[GitHubRepoResponse]:
        assert access_token == "gh-token"
        return [
            GitHubRepoResponse(
                name="private-repo",
                full_name="octocat/private-repo",
                html_url="https://github.com/octocat/private-repo",
                description=None,
                language="Go",
                stargazers_count=3,
                fork=False,
                private=True,
            ),
        ]

    monkeypatch.setattr("app.routers.github.list_user_repos", fake_list_user_repos)

    resp = await auth_client.get("/api/auth/github/repos")
    assert resp.status_code == 200
    assert resp.json()[0]["private"] is True


@pytest.mark.asyncio
async def test_auth_github_unlink(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
    admin_user: User,
) -> None:
    encrypted = encrypt_secret("gh-token", get_settings().JWT_SECRET)
    assert registry.credentials is not None
    await registry.credentials.upsert_github(
        GitHubCredential(
            user_id=admin_user.id,
            github_user_id=1,
            github_username="octocat",
            access_token=encrypted,
        ),
    )

    status_before = await auth_client.get("/api/auth/github/status")
    assert status_before.status_code == 200
    assert status_before.json()["linked"] is True

    unlink = await auth_client.delete("/api/auth/github")
    assert unlink.status_code == 200
    assert unlink.json()["linked"] is False
    assert unlink.json().get("github_username") is None

    status_after = await auth_client.get("/api/auth/github/status")
    assert status_after.status_code == 200
    assert status_after.json()["linked"] is False
