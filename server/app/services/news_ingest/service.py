"""News ingestion orchestration service."""

import asyncio

import httpx

from app.core.logging import logger
from app.core.url_safety import get_public_http_url, is_public_http_url
from app.schemas.news import (
    NewsArticleCreate,
    NewsIngestResponse,
    NewsSourceCreate,
    NewsSourceUpdate,
)
from app.services.llm_json import groq_api_key
from app.services.news import NewsService
from app.services.news_ingest.ai_summarize import (
    _feed_only_payload,
    _hash_input,
    _summarize_item,
)
from app.services.news_ingest.feed_parse import (
    _FEED_HEADERS,
    _MAX_FEED_BYTES,
    DW_FEED_URL,
    DW_HOST,
    DW_SOURCE_NAME,
    FeedItem,
    NewsSourceConfig,
    _source_from_document,
    decode_feed_body,
    load_news_sources,
    parse_feed,
)
from app.settings import get_settings


def _conditional_headers(source: NewsSourceConfig) -> dict[str, str]:
    """Build feed request headers including conditional GET validators."""
    headers = dict(_FEED_HEADERS)
    if source.etag:
        headers["If-None-Match"] = source.etag
    if source.last_modified:
        headers["If-Modified-Since"] = source.last_modified
    return headers


async def _read_feed_bytes(response: httpx.Response) -> bytes:
    """Read a feed body, aborting when it exceeds the size cap.

    ponytail: httpx 0.28 dropped request(stream=True); use aread() and
    enforce the cap after load (Content-Length still rejects oversized
    declarations early). Upgrade: client.stream() if feeds grow huge.
    """
    content_length = response.headers.get("content-length")
    if content_length is not None:
        try:
            declared_size = int(content_length)
        except ValueError:
            declared_size = None
        if declared_size is not None and declared_size > _MAX_FEED_BYTES:
            msg = "Feed response is too large"
            raise ValueError(msg)
    content = await response.aread()
    if len(content) > _MAX_FEED_BYTES:
        msg = "Feed response is too large"
        raise ValueError(msg)
    return content


class NewsIngestService:
    """Fetch trusted feeds and create curated news articles."""

    def __init__(self, news_svc: NewsService) -> None:
        """Initialize the ingestion service."""
        self.news_svc = news_svc

    async def _prepare_dw_only(self) -> None:
        """Enable Deutsche Welle English RSS only; draft seeded demo articles.

        ponytail: allowlist is DW only; drop this skip when adding a second publisher.
        """
        if self.news_svc.registry.news_sources is None:
            return
        sources = await self.news_svc.list_all_sources()
        dw = next(
            (
                source
                for source in sources
                if source.name == DW_SOURCE_NAME or source.host == DW_HOST
            ),
            None,
        )
        if dw is None:
            dw = await self.news_svc.create_source(
                NewsSourceCreate(
                    name=DW_SOURCE_NAME,
                    feed_url=DW_FEED_URL,
                    host=DW_HOST,
                    category="world",
                    region="global",
                    enabled=True,
                )
            )
        elif dw.feed_url != DW_FEED_URL or not dw.enabled or dw.host != DW_HOST:
            dw = await self.news_svc.update_source(
                dw.id,
                NewsSourceUpdate(
                    feed_url=DW_FEED_URL,
                    host=DW_HOST,
                    enabled=True,
                ),
            )
        for source in sources:
            if source.id == dw.id or not source.enabled:
                continue
            await self.news_svc.update_source(
                source.id,
                NewsSourceUpdate(enabled=False),
            )
        await self.news_svc.draft_demo_articles()

    async def _load_sources(
        self,
        source_ids: list[int] | None,
    ) -> list[NewsSourceConfig]:
        """Load DB-managed sources, falling back to settings JSON when empty."""
        if self.news_svc.registry.news_sources is not None:
            stored_sources = await self.news_svc.list_all_sources()
            if source_ids:
                allowed_ids = set(source_ids)
                stored_sources = [
                    source for source in stored_sources if source.id in allowed_ids
                ]
            if stored_sources or source_ids:
                return [_source_from_document(source) for source in stored_sources]
        return load_news_sources()

    async def _record_fetch(
        self,
        source: NewsSourceConfig,
        *,
        last_error: str | None = None,
        etag: str | None = None,
        last_modified: str | None = None,
        clear_error: bool = False,
    ) -> None:
        """Persist fetch metadata when the source is DB-backed."""
        if source.id is None:
            return
        await self.news_svc.record_source_fetch(
            source.id,
            last_error=last_error,
            etag=etag,
            last_modified=last_modified,
            clear_error=clear_error,
        )

    async def _fetch_items(
        self,
        client: httpx.AsyncClient,
        source: NewsSourceConfig,
    ) -> list[FeedItem] | None:
        """Fetch and parse one feed. Return None when the feed is unchanged (304)."""
        if not is_public_http_url(source.feed_url):
            raise ValueError("Feed URL is not allowed")
        result = await get_public_http_url(
            client,
            source.feed_url,
            headers=_conditional_headers(source),
        )
        response = result.response
        try:
            if response.status_code == 304:
                await self._record_fetch(source, clear_error=True)
                return None
            response.raise_for_status()
            if not is_public_http_url(result.url):
                raise ValueError("Feed redirect target is not allowed")
            content = await _read_feed_bytes(response)
            xml_text = decode_feed_body(content, fallback_encoding=response.encoding)
            items = parse_feed(xml_text, source)[: source.max_items_per_run]
            await self._record_fetch(
                source,
                clear_error=True,
                etag=response.headers.get("etag"),
                last_modified=response.headers.get("last-modified"),
            )
            return items
        finally:
            await response.aclose()

    async def ingest(
        self,
        *,
        actor_id: int | None = None,
        source_ids: list[int] | None = None,
    ) -> NewsIngestResponse:
        """Run ingestion for all enabled sources."""
        settings = get_settings()
        await self._prepare_dw_only()
        sources = [
            source for source in await self._load_sources(source_ids) if source.enabled
        ]
        processed = created = skipped = failed = 0
        remaining = max(1, settings.NEWS_INGEST_MAX_ITEMS_PER_RUN)
        use_groq = bool(groq_api_key())
        async with httpx.AsyncClient(timeout=15) as client:
            for source in sources:
                if remaining <= 0:
                    break
                try:
                    items = await self._fetch_items(client, source)
                except Exception as exc:
                    failed += 1
                    await self._record_fetch(source, last_error=str(exc)[:500])
                    logger.warning(
                        "News feed ingest failed",
                        context={"source": source.name, "error": str(exc)[:200]},
                    )
                    continue
                if items is None:
                    continue
                for item in items:
                    if remaining <= 0:
                        break
                    processed += 1
                    if await self.news_svc._news().source_url_exists(item.url):
                        skipped += 1
                        continue
                    try:
                        ai_model: str | None = None
                        if use_groq:
                            try:
                                ai = await _summarize_item(source, item)
                                ai_model = settings.GROQ_CHAT_MODEL
                            except Exception as exc:
                                logger.warning(
                                    "News AI summarize failed; using feed metadata",
                                    context={
                                        "source": source.name,
                                        "url": item.url,
                                        "error": str(exc)[:200],
                                    },
                                )
                                ai = _feed_only_payload(source, item)
                        else:
                            ai = _feed_only_payload(source, item)
                        article = await self.news_svc.create_article(
                            NewsArticleCreate(
                                source_id=source.id,
                                source_name=source.name,
                                source_url=item.url,
                                source_feed_url=source.feed_url,
                                source_published_at=item.published_at,
                                original_title=item.title,
                                title=ai["title"],
                                summary=ai["summary"],
                                bullets=ai["bullets"],
                                tags=ai["tags"],
                                language=source.language,
                                status="published",
                                ai_model=ai_model,
                                ai_input_hash=_hash_input(source, item),
                            ),
                            actor_id=actor_id,
                        )
                        if (
                            settings.NEWS_TELEGRAM_BOT_TOKEN
                            and settings.NEWS_TELEGRAM_CHANNEL_ID
                        ):
                            from app.workers.tasks import publish_news_telegram_task

                            await asyncio.to_thread(
                                publish_news_telegram_task.delay,
                                article.id,
                            )
                        created += 1
                        remaining -= 1
                    except Exception as exc:
                        failed += 1
                        logger.warning(
                            "News item ingest failed",
                            context={
                                "source": source.name,
                                "url": item.url,
                                "error": str(exc)[:200],
                            },
                        )
        return NewsIngestResponse(
            processed=processed,
            created=created,
            skipped=skipped,
            failed=failed,
        )
