import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.content.resume_data import RESUME_DATA
from app.db.models.search_document import SearchVisibility
from app.services.search_index import SearchDocumentInput, SearchIndexService
from app.services.search_source_types import SearchSourceType

RESUME_SOURCE_TYPE = SearchSourceType.RESUME
RESUME_PROFILE_SOURCE_ID = 1


def _skills_text(skills: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for group in skills:
        category = group.get("category", "")
        items = group.get("items", [])
        if isinstance(items, list):
            parts.append(f"{category}: {', '.join(str(item) for item in items)}")
    return "\n".join(parts)


def _resume_documents() -> list[SearchDocumentInput]:
    documents: list[SearchDocumentInput] = [
        SearchDocumentInput(
            source_type=RESUME_SOURCE_TYPE,
            source_id=RESUME_PROFILE_SOURCE_ID,
            title=f"{RESUME_DATA['name']} — {RESUME_DATA['title']}",
            body="\n".join(
                [
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
                    ],
                ),
                url="/#about",
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


async def index_resume(db: AsyncSession) -> int:
    """Upsert all resume chunks and remove stale rows. Returns document count."""
    svc = SearchIndexService(db)
    documents = _resume_documents()
    keep_ids = {document.source_id for document in documents}
    await svc.delete_stale_by_source(RESUME_SOURCE_TYPE, keep_ids)
    for document in documents:
        await svc.upsert(document)
    return len(documents)
