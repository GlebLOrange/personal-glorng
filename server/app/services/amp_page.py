import html
from typing import Any


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


CONTACT_ORDER = ("email", "telegram", "linkedin", "github")
CONTACT_LABELS = {
    "email": "Email",
    "telegram": "Telegram",
    "linkedin": "LinkedIn",
    "github": "GitHub",
}


def _contact_href(link_id: str, raw: str) -> str:
    if link_id == "email":
        return f"mailto:{raw}"
    return raw


def render_portfolio_amp(resume: dict[str, Any], canonical_url: str) -> str:
    """Render a valid AMP HTML page for the public portfolio."""
    name = _esc(resume["name"])
    title = _esc(resume["title"])
    bio = _esc(resume["bio"])
    canonical = _esc(canonical_url)

    skills_html = ""
    for group in resume.get("skills", []):
        items = ", ".join(_esc(item) for item in group.get("items", []))
        skills_html += f"""
        <section class="block">
          <h2>{_esc(group["category"])}</h2>
          <p>{items}</p>
        </section>"""

    experience_html = ""
    for job in resume.get("experience", []):
        experience_html += f"""
        <section class="block card">
          <h3>{_esc(job["role"])}</h3>
          <p class="meta">{_esc(job["company"])} · {_esc(job["period"])}</p>
          <p>{_esc(job["description"])}</p>
        </section>"""

    projects_html = ""
    for project in resume.get("projects", []):
        url = project.get("url") or ""
        link = (
            f'<a href="{_esc(url)}">{_esc(project["name"])}</a>'
            if url
            else f"<span>{_esc(project['name'])}</span>"
        )
        tech = ", ".join(_esc(t) for t in project.get("tech", []))
        projects_html += f"""
        <section class="block card">
          <h3>{link}</h3>
          <p>{_esc(project["description"])}</p>
          <p class="meta">{tech}</p>
        </section>"""

    contact_html = ""
    resume_links = resume.get("links", {})
    for link_id in CONTACT_ORDER:
        raw = (resume_links.get(link_id) or "").strip()
        if not raw:
            continue
        href = _contact_href(link_id, raw)
        label = CONTACT_LABELS[link_id]
        contact_html += f'<a class="chip" href="{_esc(href)}">{_esc(label)}</a>'

    return f"""<!doctype html>
<html ⚡ lang="en">
<head>
  <meta charset="utf-8" />
  <script async src="https://cdn.ampproject.org/v0.js"></script>
  <title>{name} — {_esc(title)}</title>
  <link rel="canonical" href="{canonical}" />
  <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1" />
  <meta name="description" content="{bio}" />
  <style amp-boilerplate>body{{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;animation:-amp-start 8s steps(1,end) 0s 1 normal both}}@-webkit-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-moz-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-ms-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@-o-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}@keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}</style>
  <noscript><style amp-boilerplate>body{{visibility:visible}}</style></noscript>
  <style amp-custom>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #141820;
      color: #f5f2ec;
      margin: 0;
      line-height: 1.6;
    }}
    .wrap {{ max-width: 42rem; margin: 0 auto; padding: 1.5rem; }}
    h1 {{
      font-size: 2rem;
      margin: 0 0 0.25rem;
      background: linear-gradient(90deg, #7bbde2, #b8a3c8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .subtitle {{ color: #c4b8ac; font-size: 1.125rem; margin: 0 0 1rem; }}
    .bio {{ color: #8a847e; font-size: 0.95rem; }}
    h2 {{
      font-size: 0.75rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #7bbde2;
      margin: 2rem 0 0.75rem;
    }}
    h3 {{ margin: 0 0 0.35rem; font-size: 1rem; }}
    .block {{ margin-bottom: 0.5rem; }}
    .card {{
      background: #1c2230;
      border: 1px solid #2e3a4e;
      border-radius: 0.5rem;
      padding: 1rem;
      margin-bottom: 0.75rem;
    }}
    .meta {{ color: #8a847e; font-size: 0.85rem; margin: 0 0 0.5rem; }}
    a {{ color: #7bbde2; text-decoration: none; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }}
    .chip {{
      border: 1px solid #2e3a4e;
      border-radius: 0.5rem;
      padding: 0.35rem 0.75rem;
      font-size: 0.85rem;
      color: #c4b8ac;
    }}
    .footer {{
      margin-top: 2.5rem;
      padding-top: 1rem;
      border-top: 1px solid #2e3a4e;
      font-size: 0.8rem;
      color: #8a847e;
    }}
    .footer a {{ color: #7bbde2; }}
  </style>
</head>
<body>
  <main class="wrap">
    <header>
      <h1>{name}</h1>
      <p class="subtitle">{title}</p>
      <p class="bio">{bio}</p>
    </header>

    <h2>Skills</h2>
    {skills_html}

    <h2>Experience</h2>
    {experience_html}

    <h2>Projects</h2>
    {projects_html}

    <h2>Contact</h2>
    <div class="chips">{contact_html}</div>

    <footer class="footer">
      <a href="{canonical}">View full portfolio</a>
    </footer>
  </main>
</body>
</html>"""
