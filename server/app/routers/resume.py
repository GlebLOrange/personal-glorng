from typing import Any

from fastapi import APIRouter

router = APIRouter()

RESUME_DATA: dict[str, Any] = {
    "name": "gLOrng",
    "title": "Full-Stack Developer",
    "bio": (
        "Building things with code. Passionate about"
        " clean architecture, developer tools, and open source."
    ),
    "skills": [
        {
            "category": "Languages",
            "items": ["Python", "TypeScript", "JavaScript"],
        },
        {
            "category": "Backend",
            "items": [
                "FastAPI",
                "SQLAlchemy",
                "Alembic",
                "PostgreSQL",
                "Redis",
                "ARQ",
            ],
        },
        {
            "category": "Frontend",
            "items": ["Vue 3", "Vite", "Tailwind CSS", "Pinia", "Vitest", "Playwright"],
        },
        {
            "category": "DevOps",
            "items": ["Docker", "Nginx", "Docker Compose", "GitHub Actions", "Linux"],
        },
    ],
    "experience": [
        {
            "role": "Full-Stack Developer",
            "company": "Freelance",
            "period": "2024 - Present",
            "description": "Building web applications, APIs, and developer tools.",
        },
    ],
    "projects": [
        {
            "name": "gLOrng Platform",
            "description": (
                "Personal platform — portfolio, admin services,"
                " Telegram todobot, and background workers on FastAPI + Vue + Docker"
            ),
            "tech": [
                "FastAPI",
                "Vue 3",
                "PostgreSQL",
                "SQLAlchemy",
                "Redis",
                "Docker",
                "ARQ",
                "Telegram",
            ],
            "url": "",
        },
    ],
    "links": {
        "github": "https://github.com/glorng",
        "telegram": "",
        "email": "admin@glorng.dev",
    },
}


@router.get(
    "",
    summary="Get resume data",
    description="Public portfolio resume content (skills, experience, projects).",
)
async def get_resume() -> dict[str, Any]:
    return RESUME_DATA
