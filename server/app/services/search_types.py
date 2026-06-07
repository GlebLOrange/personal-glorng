from dataclasses import dataclass

from app.db.documents.search import SearchVisibility


@dataclass(frozen=True)
class SearchDocumentInput:
    source_type: str
    source_id: int
    title: str
    body: str
    url: str
    visibility: SearchVisibility


@dataclass(frozen=True)
class SearchResult:
    id: int
    title: str
    body: str
    url: str
    source_type: str
    visibility: str
    source_id: int
