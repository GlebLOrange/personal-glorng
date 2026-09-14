"""Unit tests for RSS/Atom feed parsing in news ingest."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.services.news_ingest import (
    NewsSourceConfig,
    _canonical_url,
    decode_feed_body,
    parse_feed,
)


def _source() -> NewsSourceConfig:
    """Build a public feed source for parser tests."""
    return NewsSourceConfig(
        name="Example",
        feed_url="https://example.com/feed.xml",
    )


def test_parse_plain_rss20() -> None:
    """Plain RSS 2.0 items parse title, link, excerpt, and pubDate."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>Example</title>
        <item>
          <title>Hello World</title>
          <link>https://example.com/hello</link>
          <description>A short &lt;b&gt;excerpt&lt;/b&gt;.</description>
          <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """
    items = parse_feed(xml, _source())
    assert len(items) == 1
    assert items[0].title == "Hello World"
    assert items[0].url == "https://example.com/hello"
    assert items[0].excerpt == "A short excerpt ."
    assert items[0].published_at == datetime(2024, 1, 1, 12, 0, tzinfo=UTC)


def test_parse_namespaced_rss20() -> None:
    """RSS 2.0 with a default xmlns still yields items."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0" xmlns="http://backend.userland.com/rss2">
      <channel>
        <item>
          <title>Namespaced</title>
          <link>https://example.com/ns</link>
          <description>Body</description>
          <pubDate>2024-02-03T10:00:00Z</pubDate>
        </item>
      </channel>
    </rss>
    """
    items = parse_feed(xml, _source())
    assert len(items) == 1
    assert items[0].title == "Namespaced"
    assert items[0].url == "https://example.com/ns"
    assert items[0].published_at == datetime(2024, 2, 3, 10, 0, tzinfo=UTC)


def test_parse_atom_alternate_link() -> None:
    """Atom entries use rel=alternate href links."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <title>Example</title>
      <entry>
        <title>Atom Story</title>
        <link rel="self" href="https://example.com/self"/>
        <link rel="alternate" href="https://example.com/atom-story"/>
        <summary>Atom summary</summary>
        <published>2024-03-04T08:30:00Z</published>
      </entry>
    </feed>
    """
    items = parse_feed(xml, _source())
    assert len(items) == 1
    assert items[0].title == "Atom Story"
    assert items[0].url == "https://example.com/atom-story"
    assert items[0].excerpt == "Atom summary"
    assert items[0].published_at == datetime(2024, 3, 4, 8, 30, tzinfo=UTC)


def test_parse_guid_permalink_when_link_missing() -> None:
    """guid is used as the URL when link is absent and isPermaLink is true."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Guid Only</title>
          <guid isPermaLink="true">https://example.com/by-guid</guid>
          <description>via guid</description>
        </item>
      </channel>
    </rss>
    """
    items = parse_feed(xml, _source())
    assert len(items) == 1
    assert items[0].url == "https://example.com/by-guid"


def test_parse_rejects_unsafe_dtd() -> None:
    """DTD / entity declarations are rejected before parsing."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE rss [
      <!ENTITY xxe SYSTEM "file:///etc/passwd">
    ]>
    <rss version="2.0">
      <channel>
        <item>
          <title>&xxe;</title>
          <link>https://example.com/xxe</link>
        </item>
      </channel>
    </rss>
    """
    with pytest.raises(ValueError, match="DTD and entity"):
        parse_feed(xml, _source())


def test_canonical_url_strips_tracking_params() -> None:
    """Tracking query params are dropped for dedupe stability."""
    url = _canonical_url(
        "https://example.com/story?utm_source=x&id=1&fbclid=abc",
        base_url="https://example.com/feed.xml",
    )
    assert url == "https://example.com/story?id=1"


def test_decode_feed_body_prefers_xml_encoding() -> None:
    """XML encoding declaration wins over a mismatched HTTP charset hint."""
    content = '<?xml version="1.0" encoding="latin-1"?><rss/>'.encode("latin-1")
    text = decode_feed_body(content, fallback_encoding="utf-8")
    assert 'encoding="latin-1"' in text
