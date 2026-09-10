import type { ResumeData } from "@/types";

/** Static resume mirror of server/app/content/resume_data.py — keep in sync. */
export const RESUME_FALLBACK: ResumeData = {
  name: "Gleb.Y",
  title: "Python Backend / FastAPI Engineer",
  tagline:
    "Python/FastAPI backend engineer who builds production platforms" +
    " end-to-end — APIs, auth, workers, data stores, and CI/CD.",
  location: "EU",
  availability: "open to full-time and contract (remote)",
  bio:
    "I design and ship backend-heavy platforms: FastAPI services," +
    " auth and permissions, Redis/Celery workers, and deployable Docker stacks." +
    " Full-stack capable when the product needs a Vue UI — backend ownership first.",
  hiring_note:
    "For hiring managers: this site is the live product. Expect auth/RBAC," +
    " rate limits, background jobs, search indexing, OpenAPI, tests, and CI." +
    " Source and handbook links sit next to download CV above.",
  skills: [
    {
      category: "Backend",
      summary: "Production APIs, auth, workers, and service boundaries",
      items: ["Python", "FastAPI", "SQLAlchemy", "Celery", "Redis"],
    },
    {
      category: "Frontend",
      summary: "Responsive UIs with typed components and predictable state",
      items: ["Vue 3", "TypeScript", "Pinia", "Tailwind"],
    },
    {
      category: "Databases",
      summary: "Relational and document stores with caching layers",
      items: ["PostgreSQL", "MongoDB", "Redis"],
    },
    {
      category: "DevOps",
      summary: "Containerized deploys, CI/CD, and Linux ops",
      items: ["Docker", "Docker Compose", "Nginx", "CI/CD (GitHub Actions)", "Linux"],
    },
    {
      category: "Other",
      summary: "Cross-cutting concerns for production systems",
      items: [
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
      category: "Patterns",
      summary: "Maintainable architecture for long-lived codebases",
      items: ["Clean architecture", "modular services", "async processing", "event-driven tasks"],
    },
  ],
  experience: [
    {
      role: "Python Backend / Platform Engineer",
      company: "Independent — Gleb.Y platform",
      period: "2022-Present",
      description:
        "Own the FastAPI + Vue portfolio platform end-to-end (APIs, data stores, workers, and ops).",
      highlights: [
        "Built production FastAPI services with cookie auth, capability RBAC, CSRF protection, and rate limiting",
        "Shipped Celery/Redis workers for email, task automation, news ingest, and cleanup jobs",
        "Maintained 80+ server pytest modules, path-filtered GitHub Actions CI, and multi-service Docker Compose deploys",
        "Added optional Postgres/Elasticsearch search, Redis caching, OpenTelemetry hooks, and a VitePress architecture handbook",
      ],
    },
    {
      role: "Freelance Backend & Full-Stack Engineer",
      company: "Independent / client projects",
      period: "2017-2022",
      description:
        "Delivered APIs, admin tools, and automation for small teams and personal products.",
      highlights: [
        "Designed REST APIs with authentication, caching, and third-party integrations (payments, messaging)",
        "Built admin dashboards and internal automation (Telegram bots, scheduled jobs, CLI maintenance tools)",
        "Containerized deployments with Nginx reverse proxy and environment-based configuration",
        "Owned delivery from schema design through deploy — typically solo or small-team engagements",
      ],
    },
  ],
  projects: [
    {
      name: "Gleb.Y portfolio platform",
      description:
        "Problem: need a hire-ready live demo of production backend skills. " +
        "Approach: FastAPI platform with auth, workers, search, admin, and a Vue 3 client. " +
        "Outcome: public repo + handbook + OpenAPI as the primary engineering sample.",
      tech: [
        "FastAPI",
        "Vue 3",
        "MongoDB",
        "PostgreSQL",
        "Redis",
        "Celery",
        "Docker",
        "Nginx",
        "GitHub Actions",
      ],
      url: "https://github.com/GlebLOrange/personal-glorng",
    },
    {
      name: "Automation & Telegram workers",
      description:
        "Problem: notifications and async jobs without blocking the API. " +
        "Approach: Celery + Redis workers for reminders, cleanup, news ingest, and Telegram publish. " +
        "Outcome: reusable worker patterns demonstrated in the same platform.",
      tech: ["Python", "Celery", "Redis", "Telegram"],
      url: "/tools",
    },
    {
      name: "Architecture handbook & ops runbooks",
      description:
        "Problem: platform depth stays invisible to reviewers. " +
        "Approach: VitePress docs, ADRs, OpenAPI generation, and deployment runbooks. " +
        "Outcome: published handbook for hiring-manager deep-dives.",
      tech: ["VitePress", "OpenAPI", "Docker", "GitHub Actions"],
      url: "https://gleblorange.github.io/portfolio-glorng/",
    },
  ],
  education: [],
  links: {
    email: "glorange@gmail.com",
    telegram: "https://t.me/glorange",
    linkedin: "https://www.linkedin.com/in/glorange",
    github: "https://github.com/GlebLOrange",
  },
};
