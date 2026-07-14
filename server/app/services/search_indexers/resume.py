import json
from typing import Any

from app.content.resume_data import RESUME_DATA
from app.db.documents.search import SearchVisibility
from app.db.registry import DatabaseRegistry
from app.services.search_index import SearchDocumentInput, SearchIndexService
from app.services.search_source_types import SearchSourceType

RESUME_SOURCE_TYPE = SearchSourceType.RESUME
RESUME_PROFILE_SOURCE_ID = 1


def _skills_text(skills: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for group in skills:
        category = group.get("category", "")
        summary = str(group.get("summary", "")).strip()
        items = group.get("items", [])
        if isinstance(items, list):
            items_text = ", ".join(str(item) for item in items)
            if summary:
                parts.append(f"{category}: {summary} — {items_text}")
            else:
                parts.append(f"{category}: {items_text}")
    return "\n".join(parts)


def _resume_documents() -> list[SearchDocumentInput]:
    documents: list[SearchDocumentInput] = [
        SearchDocumentInput(
            source_type=RESUME_SOURCE_TYPE,
            source_id=RESUME_PROFILE_SOURCE_ID,
            title=f"{RESUME_DATA['name']} — {RESUME_DATA['title']}",
            body="\n".join(
                [
                    str(RESUME_DATA.get("tagline", "")),
                    str(RESUME_DATA.get("location", "")),
                    str(RESUME_DATA.get("availability", "")),
                    RESUME_DATA["bio"],
                    _skills_text(RESUME_DATA["skills"]),
                    json.dumps(RESUME_DATA.get("links", {})),
                ],
            ),
            url="/",
            visibility=SearchVisibility.PUBLIC,
        ),
    ]

    for index, entry in enumerate(RESUME_DATA.get("experience", []), start=1):
        documents.append(
            SearchDocumentInput(
                source_type=RESUME_SOURCE_TYPE,
                source_id=100 + index,
                title=(
                    f"{entry.get('role', 'Experience')} at {entry.get('company', '')}"
                ),
                body="\n".join(
                    [
                        str(entry.get("period", "")),
                        str(entry.get("description", "")),
                        *[
                            str(item)
                            for item in entry.get("highlights", [])
                            if isinstance(item, str)
                        ],
                    ],
                ),
                url="/#experience",
                visibility=SearchVisibility.PUBLIC,
            ),
        )

    for index, entry in enumerate(RESUME_DATA.get("education", []), start=1):
        documents.append(
            SearchDocumentInput(
                source_type=RESUME_SOURCE_TYPE,
                source_id=300 + index,
                title=(
                    f"{entry.get('degree', 'Education')} —"
                    f" {entry.get('institution', '')}"
                ),
                body="\n".join(
                    [
                        str(entry.get("period", "")),
                        str(entry.get("description", "")),
                    ],
                ),
                url="/#education",
                visibility=SearchVisibility.PUBLIC,
            ),
        )

    for index, project in enumerate(RESUME_DATA.get("projects", []), start=1):
        tech = project.get("tech", [])
        if isinstance(tech, list):
            tech_text = ", ".join(str(item) for item in tech)
        else:
            tech_text = ""
        documents.append(
            SearchDocumentInput(
                source_type=RESUME_SOURCE_TYPE,
                source_id=200 + index,
                title=str(project.get("name", "Project")),
                body="\n".join(
                    [
                        str(project.get("description", "")),
                        f"Tech: {tech_text}",
                        str(project.get("url", "")),
                    ],
                ),
                url="/#projects",
                visibility=SearchVisibility.PUBLIC,
            ),
        )

    return documents


async def index_resume(registry: DatabaseRegistry) -> int:
    """Upsert all resume chunks and remove stale rows. Returns document count."""
    svc = SearchIndexService(registry)
    documents = _resume_documents()
    keep_ids = {document.source_id for document in documents}
    await svc.delete_stale_by_source(RESUME_SOURCE_TYPE, keep_ids)
    for document in documents:
        await svc.upsert(document)
    return len(documents)
