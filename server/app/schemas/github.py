"""GitHub API schemas."""

from pydantic import BaseModel, ConfigDict, Field


class GitHubCallbackRequest(BaseModel):
    code: str = Field(min_length=1)
    state: str = Field(min_length=1)

    model_config = ConfigDict(
        json_schema_extra={"example": {"code": "abc123", "state": "csrf-token"}}
    )


class GitHubCallbackResponse(BaseModel):
    github_username: str
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "github_username": "octocat",
                "message": "GitHub account linked",
            }
        }
    )


class GitHubStatusResponse(BaseModel):
    linked: bool
    github_username: str | None = None

    model_config = ConfigDict(
        json_schema_extra={"example": {"linked": True, "github_username": "octocat"}}
    )


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
