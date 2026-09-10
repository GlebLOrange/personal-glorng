from typing import Any

RESUME_DATA: dict[str, Any] = {
    "name": "Gleb.Y",
    "title": "Python Backend / FastAPI Engineer",
    "tagline": (
        "Python/FastAPI backend engineer who builds production platforms"
        " end-to-end — APIs, auth, workers, data stores, and CI/CD."
    ),
    "location": "EU",
    "availability": "open to full-time and contract (remote)",
    "bio": (
        "I design and ship backend-heavy platforms: FastAPI services,"
        " auth and permissions, Redis/Celery workers, and deployable Docker stacks."
        " Full-stack capable when the product needs a Vue UI — backend ownership first."
    ),
    "hiring_note": (
        "For hiring managers: this site is the live product. Expect auth/RBAC,"
        " rate limits, background jobs, search indexing, OpenAPI, tests, and CI."
        " Source and handbook links sit next to download CV above."
        " Tenure note: shipping independently since 2017; the inspectable"
        " production sample is this platform (2022–present) — personal-glorng"
        " is the primary public repo."
    ),
    "skills": [
        {
            "category": "Backend",
            "summary": "Production APIs, auth, workers, and service boundaries",
            "items": [
                "Python",
                "FastAPI",
                "Motor",
                "Celery",
                "Redis",
            ],
        },
        {
            "category": "Frontend",
            "summary": "Responsive UIs with typed components and predictable state",
            "items": ["Vue 3", "TypeScript", "Pinia", "Tailwind"],
        },
        {
            "category": "Databases",
            "summary": "Document-first with optional relational search and caching",
            "items": ["MongoDB", "PostgreSQL (optional)", "Redis"],
        },
        {
            "category": "DevOps",
            "summary": "Containerized deploys, CI/CD, and Linux ops",
            "items": [
                "Docker",
                "Docker Compose",
                "Nginx",
                "CI/CD (GitHub Actions)",
                "Linux",
            ],
        },
        {
            "category": "Other",
            "summary": "Cross-cutting concerns for production systems",
            "items": [
                "API design",
                "authentication",
                "rate limiting",
                "background workers",
                "search indexing",
                "caching",
                "automation tooling",
            ],
        },
        {
            "category": "Patterns",
            "summary": "Maintainable architecture for long-lived codebases",
            "items": [
                "Clean architecture",
                "modular services",
                "async processing",
                "event-driven tasks",
            ],
        },
    ],
    "experience": [
        {
            "role": "Independent Python Backend Engineer",
            "company": "Independent — Gleb.Y platform",
            "period": "2022-Present",
            "description": (
                "Primary engineering sample: own the FastAPI + Vue platform"
                " end-to-end (APIs, MongoDB/Motor, workers, and ops)."
            ),
            "highlights": [
                (
                    "Built production FastAPI services with cookie auth,"
                    " capability RBAC, CSRF protection, and rate limiting"
                ),
                (
                    "Shipped Celery/Redis workers for email, task automation,"
                    " news ingest, and cleanup jobs"
                ),
                (
                    "Maintained 80+ server pytest modules, path-filtered"
                    " GitHub Actions CI, and multi-service Docker Compose deploys"
                ),
                (
                    "Added optional Postgres/Elasticsearch search, Redis caching,"
                    " OpenTelemetry hooks, and a VitePress architecture handbook"
                ),
            ],
        },
        {
            "role": "Freelance Backend & Full-Stack Engineer",
            "company": "Independent / client projects",
            "period": "2017-2022",
            "description": (
                "Earlier independent API/admin/automation work for small teams"
                " — less public artifact surface than the current platform."
            ),
            "highlights": [
                (
                    "Designed REST APIs with authentication, caching,"
                    " and third-party integrations (payments, messaging)"
                ),
                (
                    "Built admin dashboards and internal automation"
                    " (Telegram bots, scheduled jobs, CLI maintenance tools)"
                ),
                (
                    "Containerized deployments with Nginx reverse proxy"
                    " and environment-based configuration"
                ),
                (
                    "Owned delivery from schema design through deploy —"
                    " typically solo or small-team engagements"
                ),
            ],
        },
    ],
    "projects": [
        {
            "name": "Gleb.Y portfolio platform",
            "description": (
                "Problem: need a hire-ready live demo of production backend skills."
                " Approach: FastAPI platform with auth, Motor/MongoDB, workers,"
                " search, admin, and a Vue 3 client. Outcome: personal-glorng"
                " is the primary public engineering sample (repo + handbook + OpenAPI)."
            ),
            "tech": [
                "FastAPI",
                "Vue 3",
                "MongoDB",
                "Redis",
                "Celery",
                "Docker",
                "Nginx",
                "GitHub Actions",
            ],
            "url": "https://github.com/GlebLOrange/personal-glorng",
        },
        {
            "name": "Platform facet: Celery / Telegram workers",
            "description": (
                "Part of the Gleb.Y platform — notifications and async jobs"
                " without blocking the API. Approach: Celery + Redis workers"
                " for reminders, cleanup, news ingest, and Telegram publish."
                " Outcome: reusable worker patterns in the same codebase."
            ),
            "tech": ["Python", "Celery", "Redis", "Telegram"],
            "url": "/tools",
        },
        {
            "name": "Platform facet: architecture handbook",
            "description": (
                "Docs for the same platform — VitePress handbook, ADRs,"
                " OpenAPI generation, and deployment runbooks so reviewers"
                " can deep-dive without guessing at architecture."
            ),
            "tech": ["VitePress", "OpenAPI", "Docker", "GitHub Actions"],
            "url": "https://gleblorange.github.io/personal-glorng/",
        },
    ],
    "education": [],
    "links": {
        "email": "glorange@gmail.com",
        "telegram": "https://t.me/glorange",
        "linkedin": "https://www.linkedin.com/in/glorange",
        "github": "https://github.com/GlebLOrange",
    },
}
