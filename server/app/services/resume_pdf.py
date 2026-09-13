"""Render portfolio resume data as a downloadable PDF via WeasyPrint."""

from __future__ import annotations

import asyncio
import html
import multiprocessing
from multiprocessing.connection import Connection
from time import perf_counter
from typing import Any, cast

from app.core.exceptions import ApiError
from app.core.logging import logger

CONTACT_ORDER = ("email", "telegram", "linkedin", "github")
RESUME_PDF_RENDER_TIMEOUT_SECONDS = 30.0
_cached_pdf: bytes | None = None
_cache_lock = asyncio.Lock()


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
    return f'<p class="header-meta">{_esc(" · ".join(parts))}</p>'


def _skills_html(resume: dict[str, Any]) -> str:
    """Render grouped skills in compact rows (category + items only)."""
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
          {f'<p class="summary">{_esc(details)}</p>' if details else ""}
        </section>""",
        )
    if not blocks:
        return ""
    return f"""
  <h2>Education</h2>
  {"".join(blocks)}"""


def _contact_html(resume: dict[str, Any]) -> str:
    """Render contact links for the PDF header (middot-separated, no labels)."""
    chips: list[str] = []
    resume_links = resume.get("links", {})
    for link_id in CONTACT_ORDER:
        raw = (resume_links.get(link_id) or "").strip()
        if not raw:
            continue
        href = _contact_href(link_id, raw)
        chips.append(f'<a class="contact-item" href="{_esc(href)}">{_esc(raw)}</a>')
    return '<span class="contact-sep" aria-hidden="true">·</span>'.join(chips)


def render_resume_html(resume: dict[str, Any]) -> str:
    """Build print-ready HTML for the public resume."""
    name = _esc(resume["name"])
    title = _esc(resume["title"])
    tagline = _esc(str(resume.get("tagline", "")).strip())
    bio = _esc(resume["bio"])
    education = _education_html(resume)
    tagline_html = f'<p class="tagline">{tagline}</p>' if tagline else ""

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{name} — {title}</title>
  <style>
    @page {{
      size: A4;
      margin: 1.15cm 1.35cm;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      font-size: 9.5pt;
      line-height: 1.32;
      color: #111827;
      margin: 0;
    }}
    header {{
      border-bottom: 3px solid #7aa3d4;
      padding-bottom: 0.35rem;
      margin-bottom: 0.55rem;
    }}
    h1 {{
      font-size: 23pt;
      line-height: 1.05;
      letter-spacing: -0.03em;
      font-weight: 700;
      margin: 0 0 0.12rem;
      color: #111827;
    }}
    .title {{
      font-size: 11pt;
      font-weight: 600;
      color: #7aa3d4;
      margin: 0 0 0.12rem;
    }}
    .tagline {{
      font-size: 9pt;
      color: #4b5563;
      margin: 0 0 0.2rem;
    }}
    .header-meta {{
      font-size: 8.6pt;
      color: #6b7280;
      margin: 0 0 0.25rem;
    }}
    .bio {{
      margin: 0.28rem 0 0;
      color: #374151;
    }}
    h2 {{
      font-size: 8.2pt;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #6b7280;
      border-bottom: none;
      padding-bottom: 0;
      margin: 0.7rem 0 0.32rem;
    }}
    h2::after {{
      content: "";
      display: block;
      width: 1.6rem;
      height: 2px;
      background: #7aa3d4;
      margin-top: 0.14rem;
    }}
    h3 {{
      font-size: 9.8pt;
      margin: 0 0 0.05rem;
      color: #111827;
    }}
    .entry {{
      margin-bottom: 0.45rem;
      page-break-inside: avoid;
    }}
    .entry-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.75rem;
      margin-bottom: 0.18rem;
    }}
    .period {{
      font-size: 9pt;
      color: #9ca3af;
      white-space: nowrap;
    }}
    .subtle {{
      color: #7aa3d4;
      font-weight: 600;
      margin: 0;
    }}
    .summary {{
      margin: 0.12rem 0 0;
      color: #374151;
    }}
    .skills {{
      columns: 2;
      column-gap: 1.2rem;
    }}
    .skill-group {{
      break-inside: avoid;
      margin-bottom: 0.32rem;
    }}
    .skill-group h3 {{
      display: inline;
      font-size: 9.3pt;
      color: #111827;
      margin: 0;
    }}
    .skill-group h3::after {{
      content: ": ";
      color: #9ca3af;
    }}
    .skill-group p {{
      display: inline;
      color: #374151;
    }}
    .highlights {{
      margin: 0.2rem 0 0;
      padding-left: 0.95rem;
      color: #374151;
    }}
    .highlights li {{
      margin-bottom: 0.14rem;
    }}
    .tech {{
      color: #9ca3af;
      font-size: 8.8pt;
      margin: 0.18rem 0 0;
    }}
    a {{
      color: #7aa3d4;
      text-decoration: none;
    }}
    .contact {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.2rem 0.35rem;
      margin-top: 0.2rem;
    }}
    .contact-item {{
      font-size: 8.8pt;
      white-space: nowrap;
    }}
    .contact-sep {{
      color: #9ca3af;
      font-size: 8.8pt;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{name}</h1>
    <p class="title">{title}</p>
    {tagline_html}
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


def _render_resume_pdf_worker(
    resume: dict[str, Any],
    connection: Connection,
) -> None:
    """Render PDF in a child process and send a small result payload."""
    try:
        connection.send({"ok": True, "pdf": render_resume_pdf(resume)})
    except BaseException as exc:
        connection.send({"ok": False, "error": f"{type(exc).__name__}: {exc}"})
    finally:
        connection.close()


def _render_resume_pdf_in_subprocess(
    resume: dict[str, Any],
    timeout: float,
) -> bytes:
    """Render PDF in a killable child process."""
    context = multiprocessing.get_context("spawn")
    parent_connection, child_connection = context.Pipe(duplex=False)
    process = context.Process(
        target=_render_resume_pdf_worker,
        args=(resume, child_connection),
        daemon=True,
    )
    process.start()
    child_connection.close()

    deadline = perf_counter() + timeout
    try:
        while perf_counter() < deadline:
            if parent_connection.poll(0.1):
                result = parent_connection.recv()
                process.join(timeout=1)
                if result.get("ok"):
                    return cast(bytes, result["pdf"])
                msg = str(result.get("error") or "unknown error")
                raise RuntimeError(msg)
            if process.exitcode is not None:
                break

        if process.is_alive():
            process.terminate()
            process.join(timeout=1)
            raise TimeoutError

        raise RuntimeError(f"PDF renderer exited with code {process.exitcode}")
    finally:
        parent_connection.close()


async def get_cached_resume_pdf(resume: dict[str, Any]) -> bytes:
    """Return cached PDF bytes, rendering once per process when needed."""
    global _cached_pdf

    if _cached_pdf is not None:
        return _cached_pdf

    async with _cache_lock:
        if _cached_pdf is None:
            started_at = perf_counter()
            logger.info("Resume PDF render started")
            # ponytail: per-worker cache stays warm until restart; add invalidation
            # if resume data becomes editable at runtime.
            try:
                # ponytail: subprocess per cold render; cache keeps normal requests
                # cheap, switch to a worker queue if PDFs become user-generated.
                _cached_pdf = await asyncio.to_thread(
                    _render_resume_pdf_in_subprocess,
                    resume,
                    RESUME_PDF_RENDER_TIMEOUT_SECONDS,
                )
            except TimeoutError:
                logger.warning(
                    "Resume PDF render timed out",
                    context={"timeout_seconds": RESUME_PDF_RENDER_TIMEOUT_SECONDS},
                )
                raise ApiError(504, "Resume PDF generation timed out") from None
            except Exception as exc:
                logger.error("Resume PDF render failed", error=exc)
                raise ApiError(500, "Resume PDF generation failed") from None
            logger.info(
                "Resume PDF render completed",
                context={
                    "duration_ms": round((perf_counter() - started_at) * 1000),
                    "bytes": len(_cached_pdf),
                },
            )
        return _cached_pdf


def clear_resume_pdf_cache() -> None:
    """Clear cached PDF bytes for tests and development reloads."""
    global _cached_pdf

    _cached_pdf = None
