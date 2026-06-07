"""GitHub API response schemas."""

from pydantic import BaseModel


class GitHubRepoResponse(BaseModel):
    name: str
    full_name: str
    html_url: str
    description: str | None = None
    language: str | None = None
    stargazers_count: int
    fork: bool
    private: bool
    updated_at: str | None = None


class GitHubIssueResponse(BaseModel):
    number: int
    title: str
    html_url: str
    state: str
    repository: str
    created_at: str
    updated_at: str
