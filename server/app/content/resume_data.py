from typing import Any

RESUME_DATA: dict[str, Any] = {
    "name": "Gleb Y.",
    "title": "Full-Stack Developer",
    "tagline": "Backend-heavy full-stack — APIs, Vue frontends, Docker deployments",
    "location": "Remote · EU",
    "availability": "Open to full-time and contract (remote)",
    "bio": (
        "Full-stack developer building web applications, APIs, and the"
        " tooling around them. I work across backend services, frontends,"
        " and deployment — with a focus on code that is clear and systems"
        " that are straightforward to maintain."
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
                "Celery",
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
            "description": (
                "End-to-end delivery of web apps, APIs, and automation"
                " for clients and personal products."
            ),
            "highlights": [
                (
                    "Built and maintain this portfolio platform"
                    " (FastAPI, Vue 3, PostgreSQL/MongoDB, Redis, Celery)"
                ),
                (
                    "Ship production APIs with auth, rate limiting,"
                    " search indexing, and Docker-based deploys"
                ),
                (
                    "Develop admin tools, Telegram integrations,"
                    " and background workers for day-to-day workflows"
                ),
            ],
        },
    ],
    "projects": [
        {
            "name": "gLOrng Platform",
            "description": (
                "Personal platform — portfolio, admin services,"
                " Telegram todobot, and background workers"
                " on FastAPI + Vue + Docker"
            ),
            "tech": [
                "FastAPI",
                "Vue 3",
                "PostgreSQL",
                "SQLAlchemy",
                "Redis",
                "Docker",
                "Celery",
                "Telegram",
            ],
            "url": "https://github.com/glorange",
        },
    ],
    "education": [],
    "links": {
        "email": "glorange@gmail.com",
        "telegram": "https://t.me/glorange",
        "linkedin": "https://www.linkedin.com/in/glorange",
        "github": "https://github.com/glorange",
    },
}
