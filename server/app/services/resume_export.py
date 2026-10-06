"""Resume export and shareable-profile selection (Markdown, JSON, recruiter text)."""

from __future__ import annotations

import json
import re
from typing import Any, cast
from urllib.parse import quote

from app.content.resume_data import RESUME_DOCUMENT
from app.schemas.resume import (
    RESUME_SECTION_IDS,
    ResumeDocument,
    ResumeLinks,
    ResumeProfileSelection,
    ResumeSectionId,
    ResumeSkillGroup,
)

_PAREN_RE = re.compile(r"\([^)]*\)")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def skill_id(label: str) -> str:
    """Derive a stable skill identifier from a display label."""
    cleaned = _PAREN_RE.sub("", label.lower())
    return _NON_ALNUM_RE.sub("-", cleaned).strip("-")


def parse_csv_ids(raw: str | None) -> list[str]:
    """Split a comma-separated query value into trimmed non-empty tokens."""
    if raw is None or not raw.strip():
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def build_share_query(
    *,
    sections: list[str] | None = None,
    skills: list[str] | None = None,
    projects: list[str] | None = None,
) -> str:
    """Build a deterministic query string (sections, skills, projects; sorted values)."""
    parts: list[str] = []
    for key, values in (
        ("sections", sections or []),
        ("skills", skills or []),
        ("projects", projects or []),
    ):
        cleaned = sorted({value.strip() for value in values if value.strip()})
        if cleaned:
            # Keep commas unescaped in the share URL for readability.
            parts.append(f"{key}={quote(','.join(cleaned), safe=',')}")
    return "&".join(parts)


def select_resume(
    resume: ResumeDocument | None = None,
    *,
    skills: str | None = None,
    projects: str | None = None,
    sections: str | None = None,
) -> ResumeProfileSelection:
    """Filter the canonical resume by skill/project/section ids.

    Missing or blank params mean the full profile. Unknown ids are ignored and
    reported. If every id for a dimension is unknown, that dimension falls back
    to the full list.
    """
    source = resume or RESUME_DOCUMENT
    data = source.model_copy(deep=True)

    skill_tokens = parse_csv_ids(skills)
    project_tokens = parse_csv_ids(projects)
    section_tokens = parse_csv_ids(sections)

    known_skills = {skill_id(item) for group in data.skills for item in group.items}
    known_projects = {project.slug for project in data.projects}
    known_sections = set(RESUME_SECTION_IDS)

    ignored_skills = sorted({token for token in skill_tokens if token not in known_skills})
    ignored_projects = sorted(
        {token for token in project_tokens if token not in known_projects},
    )
    ignored_sections = sorted(
        {token for token in section_tokens if token not in known_sections},
    )

    valid_skills = [token for token in skill_tokens if token in known_skills]
    valid_projects = [token for token in project_tokens if token in known_projects]
    valid_sections = [
        cast(ResumeSectionId, token)
        for token in section_tokens
        if token in known_sections
    ]

    if skill_tokens and valid_skills:
        wanted = set(valid_skills)
        filtered_groups: list[ResumeSkillGroup] = []
        for group in data.skills:
            items = [item for item in group.items if skill_id(item) in wanted]
            if items:
                filtered_groups.append(
                    ResumeSkillGroup(
                        category=group.category,
                        summary=group.summary,
                        items=items,
                    ),
                )
        data.skills = filtered_groups

    if project_tokens and valid_projects:
        wanted_projects = set(valid_projects)
        data.projects = [
            project for project in data.projects if project.slug in wanted_projects
        ]

    if section_tokens and valid_sections:
        data = _apply_sections(data, set(valid_sections))

    return ResumeProfileSelection(
        resume=data,
        ignored_skills=ignored_skills,
        ignored_projects=ignored_projects,
        ignored_sections=ignored_sections,
    )


def _apply_sections(data: ResumeDocument, keep: set[ResumeSectionId]) -> ResumeDocument:
    """Empty sections that are not in the allowlist. Identity fields always stay."""
    result = data.model_copy(deep=True)

    if "summary" not in keep:
        result.tagline = None
        result.hiring_note = None
        result.bio = ""

    if "skills" not in keep:
        result.skills = []
    if "experience" not in keep:
        result.experience = []
    if "projects" not in keep:
        result.projects = []
    if "education" not in keep:
        result.education = []
    if "certifications" not in keep:
        result.certifications = []
    if "languages" not in keep:
        result.languages = []
    if "links" not in keep:
        result.links = ResumeLinks()

    return result


def render_resume_markdown(resume: ResumeDocument | None = None) -> str:
    """Render the canonical resume as readable Markdown."""
    doc = resume or RESUME_DOCUMENT
    lines: list[str] = [
        f"# {doc.name}",
        "",
        f"**{doc.title}**",
        "",
    ]
    meta = [part for part in (doc.location, doc.availability) if part]
    if meta:
        lines.append(" · ".join(meta))
        lines.append("")
    if doc.tagline:
        lines.append(f"*{doc.tagline}*")
        lines.append("")

    if doc.bio:
        lines.extend(["## Summary", "", doc.bio, ""])
        if doc.hiring_note:
            lines.extend([doc.hiring_note, ""])

    if doc.skills:
        lines.extend(["## Skills", ""])
        for group in doc.skills:
            lines.append(f"### {group.category}")
            if group.summary:
                lines.append("")
                lines.append(group.summary)
            lines.append("")
            for item in group.items:
                lines.append(f"- {item}")
            lines.append("")

    if doc.experience:
        lines.extend(["## Experience", ""])
        for job in doc.experience:
            lines.append(f"### {job.role} — {job.company}")
            lines.append("")
            lines.append(f"*{job.period}*")
            lines.append("")
            lines.append(job.description)
            lines.append("")
            for highlight in job.highlights:
                lines.append(f"- {highlight}")
            if job.highlights:
                lines.append("")

    if doc.projects:
        lines.extend(["## Projects", ""])
        for project in doc.projects:
            lines.append(f"### {project.name}")
            lines.append("")
            lines.append(project.description)
            lines.append("")
            if project.result:
                lines.append(f"**Result:** {project.result}")
                lines.append("")
            if project.tech:
                lines.append(f"**Tech:** {', '.join(project.tech)}")
                lines.append("")
            if project.url:
                lines.append(f"**URL:** {project.url}")
                lines.append("")

    if doc.education:
        lines.extend(["## Education", ""])
        for item in doc.education:
            lines.append(f"### {item.degree} — {item.institution}")
            lines.append("")
            lines.append(f"*{item.period}*")
            lines.append("")
            if item.description:
                lines.append(item.description)
                lines.append("")

    if doc.certifications:
        lines.extend(["## Certifications", ""])
        for item in doc.certifications:
            issuer = f" — {item.issuer}" if item.issuer else ""
            period = f" ({item.period})" if item.period else ""
            lines.append(f"- {item.name}{issuer}{period}")
        lines.append("")

    if doc.languages:
        lines.extend(["## Languages", ""])
        for item in doc.languages:
            proficiency = f" — {item.proficiency}" if item.proficiency else ""
            lines.append(f"- {item.language}{proficiency}")
        lines.append("")

    link_pairs = [
        ("Email", doc.links.email),
        ("Telegram", doc.links.telegram),
        ("LinkedIn", doc.links.linkedin),
        ("GitHub", doc.links.github),
    ]
    present = [(label, value) for label, value in link_pairs if value]
    if present:
        lines.extend(["## Links", ""])
        for label, value in present:
            lines.append(f"- **{label}:** {value}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def resume_json_bytes(resume: ResumeDocument | None = None) -> bytes:
    """Serialize the canonical resume as pretty-printed JSON bytes."""
    doc = resume or RESUME_DOCUMENT
    payload = doc.model_dump(mode="json")
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"


def build_recruiter_profile(resume: ResumeDocument | None = None) -> str:
    """Build a concise 3-5 sentence recruiter-facing profile from canonical data."""
    doc = resume or RESUME_DOCUMENT

    backend_items: list[str] = []
    for group in doc.skills:
        if group.category.lower() == "backend":
            backend_items = list(group.items)
            break
    if not backend_items:
        backend_items = [item for group in doc.skills for item in group.items][:5]

    tech_focus = ", ".join(backend_items[:5])
    location = doc.location or "remote"

    sentences: list[str] = [
        f"{doc.name} is a {doc.title} based in {location}.",
    ]
    bio_first = doc.bio.split(".", 1)[0].strip() if doc.bio else ""
    if bio_first:
        sentences.append(bio_first + ".")

    if tech_focus:
        sentences.append(f"Core stack: {tech_focus}.")

    if doc.projects:
        project_bits: list[str] = []
        for project in doc.projects[:2]:
            result = (project.result or project.description).split(".", 1)[0].strip()
            if not result:
                continue
            short = result if len(result) <= 120 else result[:117].rstrip() + "…"
            project_bits.append(f"{project.name} ({short})")
        if project_bits:
            sentences.append("Notable work: " + "; ".join(project_bits) + ".")

    if doc.hiring_note and len(sentences) < 5:
        note_first = doc.hiring_note.split(".", 1)[0].strip()
        if note_first:
            sentences.append(note_first + ".")

    return " ".join(sentences[:5]).strip()


def resume_dict_for_pdf(resume: ResumeDocument | None = None) -> dict[str, Any]:
    """Dict payload for the existing HTML/PDF renderer (no github block)."""
    doc = resume or RESUME_DOCUMENT
    return doc.model_dump(mode="json")


def profile_seo_title(selection: ResumeProfileSelection) -> str:
    """Title for shareable profile pages and OG HTML."""
    doc = selection.resume
    skill_labels = [item for group in doc.skills for item in group.items][:4]
    if skill_labels:
        return f"{doc.name} — {', '.join(skill_labels)}"
    project_names = [project.name for project in doc.projects][:2]
    if project_names:
        return f"{doc.name} — {', '.join(project_names)}"
    return f"{doc.name} — {doc.title}"


def profile_seo_description(selection: ResumeProfileSelection) -> str:
    """Description for shareable profile pages and OG HTML."""
    doc = selection.resume
    parts: list[str] = []
    if doc.bio:
        parts.append(doc.bio)
    elif doc.tagline:
        parts.append(doc.tagline)
    else:
        parts.append(f"{doc.name} — {doc.title}")
    skill_labels = [item for group in doc.skills for item in group.items][:6]
    if skill_labels:
        parts.append("Skills: " + ", ".join(skill_labels) + ".")
    project_names = [project.name for project in doc.projects][:3]
    if project_names:
        parts.append("Projects: " + ", ".join(project_names) + ".")
    return " ".join(parts)[:300]
