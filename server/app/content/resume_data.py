from typing import Any

RESUME_DATA: dict[str, Any] = {
    "name": "Gleb.Y",
    "title": "Python Backend / FastAPI Engineer",
    "tagline": (
        "I build production APIs, auth, workers, and deploys"
        " — this site is a live example."
    ),
    "location": "Wrocław, Poland",
    "availability": "open to full-time and contract (remote)",
    "bio": (
        "Backend-first: FastAPI, auth, Redis/Celery, Docker."
        " I own a Vue UI when the product needs one."
    ),
    "hiring_note": (
        "This site is the live product — auth, jobs, search, OpenAPI, tests, and CI."
        " Independent since 2017; this personal website (2022-present)"
        " is the public sample."
    ),
    "skills": [
        {
            "category": "Backend",
            "summary": "Production APIs, auth, workers, and service boundaries",
            "items": [
                "Python",
                "FastAPI",
                "Pydantic",
                "SQLAlchemy",
                "Motor",
                "Celery",
                "Redis",
                "RabbitMQ",
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
            "items": ["MongoDB", "PostgreSQL", "Redis", "Elasticsearch", "SQL"],
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
                "pytest",
                "Ruff",
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
            "company": "Independent — personal website",
            "period": "2022-Present",
            "description": (
                "Operate this FastAPI + Vue platform as a public hiring sample:"
                " cookie auth, CSRF, SSRF-safe fetches, workers, and CI."
            ),
            "highlights": [
                (
                    "Cookie auth with capability RBAC, CSRF origin checks on"
                    " mutating /api (staging/production), and fail-closed rate limits"
                ),
                (
                    "SSRF-safe outbound HTTP: public DNS off the event loop,"
                    " TLS SNI preserved on IP connect, redirect hop re-validation"
                ),
                (
                    "Celery/Redis workers for email, task automation,"
                    " news ingest, and cleanup without blocking the API"
                ),
                (
                    "Path-filtered GitHub Actions CI, multi-service Docker Compose,"
                    " OpenAPI, and a VitePress architecture handbook"
                ),
                (
                    "Application monitoring and error tracking with Sentry"
                    " and OpenTelemetry instrumentation"
                ),
            ],
        },
        {
            "role": "Freelance Backend & Full-Stack Engineer",
            "company": "Independent / client projects",
            "period": "2017-2022",
            "description": "API, admin, and automation work for small teams.",
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
            "name": "cookie auth & CSRF",
            "description": (
                "Browser sessions on this SPA need CSRF protection without"
                " breaking Bearer-token API clients."
            ),
            "problem": (
                "Cookie auth on a Vue SPA is vulnerable to cross-site request"
                " forgery unless mutating API calls check Origin; Bearer clients"
                " must keep working."
            ),
            "approach": (
                "HttpOnly cookie sessions with capability RBAC; CSRF origin"
                " checks on mutating /api in staging and production; Bearer-only"
                " requests skip CSRF; auth rate limits fail closed when Redis is down."
            ),
            "result": (
                "Documented security path with CSRF middleware tests;"
                " bad Origin rejected in production; Bearer automation unaffected."
            ),
            "tech": ["FastAPI", "cookies", "CSRF", "RBAC", "Redis"],
            "url": (
                "https://gleblorange.github.io/personal-glorng/"
                "reference/security.html#csrf-and-cors"
            ),
        },
        {
            "name": "SSRF-safe outbound fetch",
            "description": (
                "Server-side HTTP for news and health checks must not reach"
                " private networks, and must keep TLS correct after DNS pin."
            ),
            "problem": (
                "Connecting to a resolved IP without SNI fails HTTPS verification;"
                " joining redirects against the IP URL drops the original host."
            ),
            "approach": (
                "get_public_http_url resolves public DNS in asyncio.to_thread,"
                " connects to that IP with Host + sni_hostname, re-validates every"
                " hop, and joins Location against the pre-rewrite URL."
            ),
            "result": (
                "Fail-closed public fetch with unit coverage for SNI, relative"
                " redirects, and off-loop DNS — used by outbound tool paths."
            ),
            "tech": ["Python", "httpx", "asyncio", "DNS"],
            "url": (
                "https://github.com/GlebLOrange/personal-glorng/blob/main/"
                "server/app/core/url_safety.py"
            ),
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
