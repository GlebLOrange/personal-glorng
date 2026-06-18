"""Render portfolio resume data as a downloadable PDF via WeasyPrint."""

from __future__ import annotations

import html
from typing import Any

CONTACT_ORDER = ("email", "telegram", "linkedin", "github")
CONTACT_LABELS = {
    "email": "Email",
    "telegram": "Telegram",
    "linkedin": "LinkedIn",
    "github": "GitHub",
}


def _esc(value: str) -> str:
    """Escape plain text for safe HTML output."""
    return html.escape(value, quote=True)


def _contact_href(link_id: str, raw: str) -> str:
    """Return the href target for a resume contact link."""
    if link_id == "email":
        return f"mailto:{raw}"
    return raw


def _highlights_html(highlights: list[Any]) -> str:
    """Render bullet highlights when valid strings are present."""
    items = [_esc(str(item)) for item in highlights if isinstance(item, str) and item]
    if not items:
        return ""
    bullets = "".join(f"<li>{item}</li>" for item in items)
    return f'<ul class="highlights">{bullets}</ul>'


def _header_meta_line(resume: dict[str, Any]) -> str:
    """Render location and availability as a compact header line."""
    location = str(resume.get("location", "")).strip()
    availability = str(resume.get("availability", "")).strip()
    if not location and not availability:
        return ""
    parts = [part for part in (location, availability) if part]
    return f'<p class="header-meta">{_esc(" | ".join(parts))}</p>'


def _skills_html(resume: dict[str, Any]) -> str:
    """Render grouped skills in compact rows."""
    blocks: list[str] = []
    for group in resume.get("skills", []):
        items = ", ".join(_esc(item) for item in group.get("items", []))
        blocks.append(
            f"""
        <div class="skill-group">
          <h3>{_esc(group["category"])}</h3>
          <p>{items}</p>
        </div>""",
        )
    return "".join(blocks)


def _experience_html(resume: dict[str, Any]) -> str:
    """Render work history entries."""
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
              <p class="subtle">{_esc(job["company"])}</p>
            </div>
            <span class="period">{_esc(job["period"])}</span>
          </div>
          {description_html}
          {highlights}
        </section>""",
        )
    return "".join(blocks)


def _projects_html(resume: dict[str, Any]) -> str:
    """Render selected project entries."""
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
          <p class="summary">{_esc(project["description"])}</p>
          <p class="tech">{tech}</p>
        </section>""",
        )
    return "".join(blocks)


def _education_html(resume: dict[str, Any]) -> str:
    """Render education entries when resume data provides them."""
    blocks: list[str] = []
    for item in resume.get("education", []):
        name = str(item.get("name", "")).strip()
        degree = str(item.get("degree", "")).strip()
        period = str(item.get("period", "")).strip()
        details = str(item.get("details", "")).strip()
        if not name and not degree:
            continue
        blocks.append(
            f"""
        <section class="entry">
          <div class="entry-header">
            <div>
              <h3>{_esc(degree or name)}</h3>
              <p class="subtle">{_esc(name)}</p>
            </div>
            <span class="period">{_esc(period)}</span>
          </div>
          {f'<p class="summary">{_esc(details)}</p>' if details else ''}
        </section>""",
        )
    if not blocks:
        return ""
    return f"""
  <h2>Education</h2>
  {''.join(blocks)}"""


def _contact_html(resume: dict[str, Any]) -> str:
    """Render contact links for the PDF header."""
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
            f'<span>{_esc(label)}</span> '
            f'<a href="{_esc(href)}">{_esc(raw)}</a>'
            f"</span>",
        )
    return "".join(chips)


def render_resume_html(resume: dict[str, Any]) -> str:
    """Build print-ready HTML for the public resume."""
    name = _esc(resume["name"])
    title = _esc(resume["title"])
    bio = _esc(resume["bio"])
    education = _education_html(resume)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{name} — {title}</title>
  <style>
    @page {{
      size: A4;
      margin: 1.25cm 1.35cm;
    }}
    body {{
      font-family: Arial, Helvetica, sans-serif;
      font-size: 9.7pt;
      line-height: 1.36;
      color: #172033;
      margin: 0;
    }}
    header {{
      border-bottom: 2px solid #1f4f78;
      padding-bottom: 0.45rem;
      margin-bottom: 0.75rem;
    }}
    h1 {{
      font-size: 24pt;
      line-height: 1;
      letter-spacing: -0.03em;
      margin: 0 0 0.18rem;
      color: #0b1220;
    }}
    .title {{
      font-size: 12.5pt;
      font-weight: 700;
      color: #1f4f78;
      margin: 0 0 0.22rem;
    }}
    .header-meta {{
      font-size: 9.5pt;
      color: #46566f;
      margin: 0 0 0.45rem;
    }}
    .bio {{
      margin: 0.45rem 0 0;
      color: #263447;
    }}
    h2 {{
      font-size: 8.5pt;
      letter-spacing: 0.09em;
      text-transform: uppercase;
      color: #1f4f78;
      border-bottom: 1px solid #cfd8e3;
      padding-bottom: 0.14rem;
      margin: 0.82rem 0 0.38rem;
    }}
    h3 {{
      font-size: 10pt;
      margin: 0 0 0.06rem;
      color: #0b1220;
    }}
    .entry {{
      margin-bottom: 0.55rem;
      page-break-inside: avoid;
    }}
    .entry-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.75rem;
      margin-bottom: 0.16rem;
    }}
    .period {{
      font-size: 8.8pt;
      color: #607086;
      white-space: nowrap;
    }}
    .subtle {{
      color: #1f4f78;
      font-weight: 700;
      margin: 0;
    }}
    .summary {{
      margin: 0.1rem 0 0;
    }}
    .skills {{
      columns: 2;
      column-gap: 1.2rem;
    }}
    .skill-group {{
      break-inside: avoid;
      margin-bottom: 0.28rem;
    }}
    .skill-group h3 {{
      display: inline;
      font-size: 9.2pt;
      color: #0b1220;
      margin: 0;
    }}
    .skill-group h3::after {{
      content: ": ";
      color: #607086;
    }}
    .skill-group p {{
      display: inline;
      color: #263447;
    }}
    .highlights {{
      margin: 0.18rem 0 0;
      padding-left: 0.95rem;
      color: #263447;
    }}
    .highlights li {{
      margin-bottom: 0.12rem;
    }}
    .tech {{
      color: #607086;
      font-size: 8.8pt;
      margin: 0.16rem 0 0;
    }}
    a {{
      color: #1f4f78;
      text-decoration: none;
    }}
    .contact {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.16rem 0.7rem;
      margin-top: 0.35rem;
    }}
    .contact-item {{
      font-size: 8.7pt;
      white-space: nowrap;
    }}
    .contact-item span {{
      color: #607086;
      font-weight: 700;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{name}</h1>
    <p class="title">{title}</p>
    {_header_meta_line(resume)}
    <div class="contact">{_contact_html(resume)}</div>
    <p class="bio">{bio}</p>
  </header>

  <h2>Skills</h2>
  <section class="skills">{_skills_html(resume)}</section>

  <h2>Experience</h2>
  {_experience_html(resume)}

  <h2>Projects</h2>
  {_projects_html(resume)}

  {education}
</body>
</html>"""


def render_resume_pdf(resume: dict[str, Any]) -> bytes:
    """Render resume dict to PDF bytes."""
    from weasyprint import HTML

    document = HTML(string=render_resume_html(resume))
    return document.write_pdf()
