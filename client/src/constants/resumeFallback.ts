import type { ResumeData } from "@/types";

/** Static resume mirror of server/app/content/resume_data.py — keep in sync. */
export const RESUME_FALLBACK: ResumeData = {
  name: "Gleb.Y",
  title: "Python Backend / FastAPI Engineer",
  tagline:
    "I build production APIs, auth, workers, and deploys" +
    " — this site is a live example.",
  location: "EU",
  availability: "open to full-time and contract (remote)",
  bio:
    "Backend-first: FastAPI, auth, Redis/Celery, Docker." +
    " I own a Vue UI when the product needs one.",
  hiring_note:
    "This site is the live product — auth, jobs, search, OpenAPI, tests, and CI." +
    " Source and handbook sit next to download CV." +
    " Independent since 2017; this personal website (2022–present)" +
    " is the public sample.",
  skills: [
    {
      category: "Backend",
      summary: "Production APIs, auth, workers, and service boundaries",
      items: ["Python", "FastAPI", "Motor", "Celery", "Redis"],
    },
    {
      category: "Frontend",
      summary: "Responsive UIs with typed components and predictable state",
      items: ["Vue 3", "TypeScript", "Pinia", "Tailwind"],
    },
    {
      category: "Databases",
      summary: "Document-first with optional relational search and caching",
      items: ["MongoDB", "PostgreSQL (optional)", "Redis"],
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
      role: "Independent Python Backend Engineer",
      company: "Independent — personal website",
      period: "2022-Present",
      description:
        "Built and operate this FastAPI + Vue site as a production sample" +
        " (APIs, MongoDB, workers, ops).",
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
      description: "API, admin, and automation work for small teams.",
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
      name: "personal website",
      description:
        "Public engineering sample: FastAPI + Vue with auth, workers," +
        " search, admin, OpenAPI, and a handbook (repo linked).",
      tech: [
        "FastAPI",
        "Vue 3",
        "MongoDB",
        "Redis",
        "Celery",
        "Docker",
        "Nginx",
        "GitHub Actions",
      ],
      url: "https://github.com/GlebLOrange/personal-glorng",
    },
    {
      name: "background jobs & telegram",
      description:
        "Celery + Redis workers for reminders, cleanup, news ingest," +
        " and Telegram publish without blocking the API.",
      tech: ["Python", "Celery", "Redis", "Telegram"],
      url: "/tools",
    },
    {
      name: "architecture handbook",
      description:
        "VitePress handbook, ADRs, OpenAPI generation, and deployment" +
        " runbooks for reviewers.",
      tech: ["VitePress", "OpenAPI", "Docker", "GitHub Actions"],
      url: "https://gleblorange.github.io/personal-glorng/",
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
