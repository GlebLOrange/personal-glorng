"""Render portfolio resume data as a downloadable PDF via WeasyPrint."""

from __future__ import annotations

import html
from typing import Any

from weasyprint import HTML

CONTACT_ORDER = ("email", "telegram", "linkedin", "github")
CONTACT_LABELS = {
    "email": "Email",
    "telegram": "Telegram",
    "linkedin": "LinkedIn",
    "github": "GitHub",
}


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


def _contact_href(link_id: str, raw: str) -> str:
    if link_id == "email":
        return f"mailto:{raw}"
    return raw


def _highlights_html(highlights: list[Any]) -> str:
    items = [_esc(str(item)) for item in highlights if isinstance(item, str) and item]
    if not items:
        return ""
    bullets = "".join(f"<li>{item}</li>" for item in items)
    return f'<ul class="highlights">{bullets}</ul>'


def _header_meta_line(resume: dict[str, Any]) -> str:
    location = str(resume.get("location", "")).strip()
    availability = str(resume.get("availability", "")).strip()
    if not location and not availability:
        return ""
    parts = [part for part in (location, availability) if part]
    return f'<p class="meta">{_esc(" · ".join(parts))}</p>'


def _skills_html(resume: dict[str, Any]) -> str:
    blocks: list[str] = []
    for group in resume.get("skills", []):
        items = ", ".join(_esc(item) for item in group.get("items", []))
        blocks.append(
            f"""
        <section class="skill-group">
          <h3>{_esc(group["category"])}</h3>
          <p>{items}</p>
        </section>""",
        )
    return "".join(blocks)


def _experience_html(resume: dict[str, Any]) -> str:
    blocks: list[str] = []
    for job in resume.get("experience", []):
        description = str(job.get("description", "")).strip()
        description_html = f"<p>{_esc(description)}</p>" if description else ""
        highlights = _highlights_html(job.get("highlights", []))
        blocks.append(
            f"""
        <section class="entry">
          <div class="entry-header">
            <div>
              <h3>{_esc(job["role"])}</h3>
              <p class="company">{_esc(job["company"])}</p>
            </div>
            <span class="period">{_esc(job["period"])}</span>
          </div>
          {description_html}
          {highlights}
        </section>""",
        )
    return "".join(blocks)


def _projects_html(resume: dict[str, Any]) -> str:
    blocks: list[str] = []
    for project in resume.get("projects", []):
        tech = ", ".join(_esc(t) for t in project.get("tech", []))
        url = str(project.get("url", "")).strip()
        link_html = (
            f'<a href="{_esc(url)}">{_esc(project["name"])}</a>'
            if url
            else f"<span>{_esc(project['name'])}</span>"
        )
        blocks.append(
            f"""
        <section class="entry">
          <h3>{link_html}</h3>
          <p>{_esc(project["description"])}</p>
          <p class="meta">{tech}</p>
        </section>""",
        )
    return "".join(blocks)


def _contact_html(resume: dict[str, Any]) -> str:
    chips: list[str] = []
    resume_links = resume.get("links", {})
    for link_id in CONTACT_ORDER:
        raw = (resume_links.get(link_id) or "").strip()
        if not raw:
            continue
        href = _contact_href(link_id, raw)
        label = CONTACT_LABELS[link_id]
        chips.append(
            f'<span class="contact-item">'
            f'<strong>{_esc(label)}:</strong> '
            f'<a href="{_esc(href)}">{_esc(raw)}</a>'
            f"</span>",
        )
    return "".join(chips)


def render_resume_html(resume: dict[str, Any]) -> str:
    """Build print-ready HTML for the public resume."""
    name = _esc(resume["name"])
    title = _esc(resume["title"])
    bio = _esc(resume["bio"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{name} — {title}</title>
  <style>
    @page {{
      size: A4;
      margin: 1.6cm 1.8cm;
    }}
    body {{
      font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.45;
      color: #1a1a1a;
      margin: 0;
    }}
    h1 {{
      font-size: 22pt;
      margin: 0 0 0.15rem;
      color: #111;
    }}
    .title {{
      font-size: 13pt;
      color: #333;
      margin: 0 0 0.35rem;
    }}
    .meta {{
      font-size: 9.5pt;
      color: #555;
      margin: 0 0 0.75rem;
    }}
    .bio {{
      margin: 0 0 1rem;
      color: #333;
    }}
    h2 {{
      font-size: 9pt;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: #2563eb;
      border-bottom: 1px solid #ddd;
      padding-bottom: 0.2rem;
      margin: 1.1rem 0 0.55rem;
    }}
    h3 {{
      font-size: 11pt;
      margin: 0 0 0.15rem;
      color: #111;
    }}
    .company {{
      font-size: 10pt;
      color: #2563eb;
      margin: 0;
    }}
    .entry {{
      margin-bottom: 0.75rem;
      page-break-inside: avoid;
    }}
    .entry-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
      margin-bottom: 0.25rem;
    }}
    .period {{
      font-size: 9.5pt;
      color: #666;
      white-space: nowrap;
    }}
    .skill-group {{
      margin-bottom: 0.45rem;
    }}
    .skill-group h3 {{
      font-size: 10pt;
      margin-bottom: 0.1rem;
    }}
    .skill-group p {{
      margin: 0;
      color: #333;
    }}
    .highlights {{
      margin: 0.35rem 0 0;
      padding-left: 1.1rem;
      color: #333;
    }}
    .highlights li {{
      margin-bottom: 0.2rem;
    }}
    a {{
      color: #2563eb;
      text-decoration: none;
    }}
    .contact {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem 1.25rem;
    }}
    .contact-item {{
      font-size: 9.5pt;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{name}</h1>
    <p class="title">{title}</p>
    {_header_meta_line(resume)}
    <p class="bio">{bio}</p>
  </header>

  <h2>Skills</h2>
  {_skills_html(resume)}

  <h2>Experience</h2>
  {_experience_html(resume)}

  <h2>Projects</h2>
  {_projects_html(resume)}

  <h2>Contact</h2>
  <div class="contact">{_contact_html(resume)}</div>
</body>
</html>"""


def render_resume_pdf(resume: dict[str, Any]) -> bytes:
    """Render resume dict to PDF bytes."""
    document = HTML(string=render_resume_html(resume))
    return document.write_pdf()
