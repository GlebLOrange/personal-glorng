from typing import Any

RESUME_DATA: dict[str, Any] = {
    "name": "Gleb.Y",
    "title": "Full-Stack Developer",
    "location": "Remote · EU",
    "availability": "Open to full-time and contract (remote)",
    "bio": (
        "End-to-end delivery of web apps, APIs, and automation for clients"
        " and personal products. I build clean, maintainable systems across"
        " backend, frontend, and deployment — with a focus on clarity,"
        " reliability, and long-term maintainability."
    ),
    "skills": [
        {
            "category": "Backend",
            "items": [
                "Python",
                "FastAPI",
                "Django",
                "SQLAlchemy",
                "Celery",
                "Redis",
            ],
        },
        {
            "category": "Frontend",
            "items": ["Vue 3", "TypeScript", "Pinia", "Tailwind"],
        },
        {
            "category": "Databases",
            "items": ["PostgreSQL", "MongoDB", "Redis"],
        },
        {
            "category": "DevOps",
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
            "role": "Full-Stack Developer",
            "company": "Freelance / Independent",
            "period": "2017-Present",
            "description": "",
            "highlights": [
                (
                    "Deliver complete web applications, backend services,"
                    " and automation tools for clients"
                ),
                (
                    "Design and ship production APIs with authentication,"
                    " rate limiting, caching, and monitoring"
                ),
                (
                    "Build admin dashboards, internal tools, and workflow"
                    " automation (Celery, Redis, Telegram bots)"
                ),
                (
                    "Implement CI/CD pipelines, containerized deployments,"
                    " and environment-based configuration"
                ),
                (
                    "Integrate third-party services (payments, messaging,"
                    " analytics, search engines)"
                ),
            ],
        },
    ],
    "projects": [
        {
            "name": "Portfolio Platform",
            "description": (
                "Built and maintain a full platform powering personal"
                " projects, blog, and API demos. Backend includes auth,"
                " rate limiting, search indexing, background workers,"
                " and caching. Frontend built with Vue 3 + TypeScript,"
                " fully responsive and optimized. Automated deployments"
                " with Docker, Nginx, and GitHub Actions."
            ),
            "tech": [
                "FastAPI",
                "Vue 3",
                "PostgreSQL",
                "MongoDB",
                "Redis",
                "Celery",
                "Docker",
                "Nginx",
                "GitHub Actions",
            ],
            "url": "https://github.com/glorange",
        },
        {
            "name": "API-Driven Automation Tools",
            "description": (
                "Developed Telegram integrations for notifications, task"
                " automation, and admin workflows. Built background workers"
                " for scheduled jobs, data processing, and async tasks."
                " Created internal CLI tools for deployments, migrations,"
                " and maintenance."
            ),
            "tech": ["Telegram", "Celery", "Redis", "Python"],
            "url": "",
        },
        {
            "name": "Client Web Applications",
            "description": (
                "Delivered full-stack apps with dashboards, CRUD flows,"
                " and real-time features. Implemented secure"
                " authentication, RBAC, and audit logging. Optimized"
                " database queries, caching layers, and API performance."
            ),
            "tech": ["FastAPI", "Vue 3", "PostgreSQL", "Redis"],
            "url": "",
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
