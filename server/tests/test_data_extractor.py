"""Tests for unified file data extraction."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from httpx import AsyncClient

from app.core.data_extractor import extract
from app.core.data_extractor.format import resolve_format, sniff_format
from app.core.data_extractor.profiles import apply_profile
from app.core.data_extractor.types import DataFormat, ExtractOptions
from app.core.exceptions import ValidationError

CSV_SAMPLE = "name,amount\napple,1.50\nbanana,0.75\n"
JSON_ARRAY = '[{"id": 1, "name": "alpha"}, {"id": 2, "name": "beta"}]'
JSON_OBJECT = '{"id": 1, "name": "solo"}'
JSON_SCALARS = "[1, 2, 3]"
XML_ROWS = """\
<items>
  <item id="1"><name>alpha</name></item>
  <item id="2"><name>beta</name></item>
</items>
"""
XML_TREE = "<root><child>value</child></root>"


def test_extract_csv_from_bytes() -> None:
    result = extract(CSV_SAMPLE.encode(), filename="data.csv")
    assert result.format is DataFormat.CSV
    assert result.records == [
        {"name": "apple", "amount": "1.50"},
        {"name": "banana", "amount": "0.75"},
    ]
    assert result.meta["columns"] == ["name", "amount"]
    assert result.meta["row_count"] == 2


def test_extract_csv_from_path(tmp_path: Path) -> None:
    file_path = tmp_path / "data.csv"
    file_path.write_text(CSV_SAMPLE, encoding="utf-8")
    result = extract(file_path)
    assert result.format is DataFormat.CSV
    assert len(result.records) == 2


def test_extract_json_array() -> None:
    result = extract(JSON_ARRAY.encode(), filename="data.json")
    assert result.format is DataFormat.JSON
    assert len(result.records) == 2
    assert result.meta["columns"] == ["id", "name"]


def test_extract_json_object() -> None:
    result = extract(JSON_OBJECT.encode(), filename="data.json")
    assert result.records == [{"id": 1, "name": "solo"}]
    assert result.meta["row_count"] == 1


def test_extract_json_scalar_list() -> None:
    result = extract(JSON_SCALARS.encode(), filename="data.json")
    assert result.records == [{"value": 1}, {"value": 2}, {"value": 3}]
    assert result.meta["value_type"] == "int"
    assert result.meta["columns"] == ["value"]


def test_extract_xml_rows_auto_detect() -> None:
    result = extract(XML_ROWS.encode(), filename="feed.xml")
    assert result.format is DataFormat.XML
    assert len(result.records) == 2
    assert result.meta["row_tag"] == "item"
    assert result.records[0]["id"] == "1"
    assert result.records[0]["name"] == "alpha"


def test_extract_xml_rows_with_row_tag() -> None:
    options = ExtractOptions(row_tag="item")
    result = extract(XML_ROWS.encode(), filename="feed.xml", options=options)
    assert len(result.records) == 2
    assert result.meta["row_tag"] == "item"


def test_extract_xml_tree_mode() -> None:
    options = ExtractOptions(xml_mode="tree")
    result = extract(XML_TREE.encode(), filename="feed.xml", options=options)
    assert result.meta["xml_mode"] == "tree"
    assert len(result.records) == 1
    assert "root" in result.records[0]


def test_sniff_format_from_extension() -> None:
    assert sniff_format("report.CSV") is DataFormat.CSV
    assert sniff_format("data.tsv") is DataFormat.CSV
    assert sniff_format("payload.json") is DataFormat.JSON
    assert sniff_format("feed.xml") is DataFormat.XML


def test_resolve_format_prefers_explicit_value() -> None:
    assert resolve_format("json", filename="data.csv") is DataFormat.JSON


def test_extract_unknown_extension_without_format() -> None:
    with pytest.raises(ValidationError, match="Cannot detect format"):
        extract(b"hello", filename="notes.txt")


def test_extract_bytes_without_filename_or_format() -> None:
    with pytest.raises(ValidationError, match="filename is required"):
        extract(b"{}")


def test_extract_invalid_json() -> None:
    with pytest.raises(ValidationError, match="Invalid JSON"):
        extract(b"{bad", filename="broken.json")


def test_extract_invalid_xml() -> None:
    with pytest.raises(ValidationError, match="Invalid XML"):
        extract(b"<root>", filename="broken.xml")


def test_extract_xml_rejects_dtd() -> None:
    xml = (
        '<?xml version="1.0"?>'
        "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>"
        "<root>&xxe;</root>"
    )
    with pytest.raises(ValidationError, match=r"DTD|entity|Invalid XML"):
        extract(xml.encode(), filename="xxe.xml")


def test_extract_xml_rejects_entity_after_padding() -> None:
    # Pre-check only scans first 4k; parser-level defusedxml must still reject.
    padding = "<!--" + ("x" * 5000) + "-->"
    xml = (
        f"{padding}"
        "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>"
        "<root>&xxe;</root>"
    )
    with pytest.raises(
        ValidationError,
        match=r"DTD|entity|Invalid XML|not supported",
    ):
        extract(xml.encode(), filename="padded-xxe.xml")


def test_extract_csv_without_header() -> None:
    with pytest.raises(ValidationError, match="no header row"):
        extract(b"1,2\n3,4", filename="data.csv")


def test_extract_xml_missing_row_tag() -> None:
    xml = "<items><only>one</only></items>"
    options = ExtractOptions(row_tag="missing")
    with pytest.raises(ValidationError, match="No XML elements found"):
        extract(xml.encode(), filename="feed.xml", options=options)


@pytest.mark.asyncio
async def test_extract_api_csv(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/tools/data-extract",
        files={"file": ("sample.csv", BytesIO(CSV_SAMPLE.encode()), "text/csv")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["format"] == "csv"
    assert payload["meta"]["row_count"] == 2
    assert payload["records"][0]["name"] == "apple"


PIPE_EMBED_LINE = (
    '<iframe src="https://example.com/embed/abc123"></iframe>|'
    "https://example.com/thumb.jpg|"
    "https://example.com/p1.jpg;https://example.com/p2.jpg|"
    "Sample title|"
    "tag1;tag2|"
    "cat1|"
    "actor1|"
    "channel|"
    "120|"
    "1000|"
    "80|"
    "20|"
    "https://example.com/thumbs/"
)


def test_extract_delimited_pipe_embed_profile() -> None:
    options = apply_profile("pipe_embed", ExtractOptions())
    result = extract(
        PIPE_EMBED_LINE.encode(),
        "delimited",
        filename="feed.pipe",
        options=options,
    )
    assert result.format is DataFormat.DELIMITED
    assert len(result.records) == 1
    record = result.records[0]
    assert record["embed_id"] == "abc123"
    assert record["title"] == "Sample title"
    assert record["tags"] == ["tag1", "tag2"]
    assert record["rating_percent"] == 80.0


def test_extract_delimited_skips_bad_line_with_profile() -> None:
    content = f"{PIPE_EMBED_LINE}\nnot-enough-fields\n"
    options = apply_profile("pipe_embed", ExtractOptions())
    result = extract(
        content.encode(), "delimited", filename="feed.pipe", options=options
    )
    assert len(result.records) == 1
    assert result.meta["error_count"] == 1


@pytest.mark.asyncio
async def test_import_api_csv(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/tools/data-extract/import",
        files={"file": ("sample.csv", BytesIO(CSV_SAMPLE.encode()), "text/csv")},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["row_count"] == 2
    assert payload["batch_id"] > 0
    assert len(payload["preview"]) == 2


@pytest.mark.asyncio
async def test_list_import_batches(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/tools/data-extract/import",
        files={"file": ("sample.csv", BytesIO(CSV_SAMPLE.encode()), "text/csv")},
    )
    response = await auth_client.get("/api/tools/data-extract/batches")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert payload["per_page"] == 9
    assert payload["items"][0]["filename"] == "sample.csv"


@pytest.mark.asyncio
async def test_get_import_batch_detail(auth_client: AsyncClient) -> None:
    created = await auth_client.post(
        "/api/tools/data-extract/import",
        files={"file": ("sample.csv", BytesIO(CSV_SAMPLE.encode()), "text/csv")},
    )
    batch_id = created.json()["batch_id"]
    response = await auth_client.get(f"/api/tools/data-extract/batches/{batch_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["batch"]["id"] == batch_id
    assert len(payload["preview_rows"]) == 2


@pytest.mark.asyncio
async def test_import_batch_ownership_denied(
    client: AsyncClient,
    registry: object,
) -> None:
    from app.core.security import create_access_token
    from app.db.registry import DatabaseRegistry
    from tests.factories import create_user

    db_registry: DatabaseRegistry = registry  # type: ignore[assignment]
    owner = await create_user(
        db_registry,
        email="import-owner@glorng.dev",
        permissions=["data-extract:read", "data-extract:write"],
    )
    other = await create_user(
        db_registry,
        email="import-other@glorng.dev",
        permissions=["data-extract:read", "data-extract:write"],
    )
    owner_token = create_access_token(str(owner.public_id), user_id=owner.id)
    other_token = create_access_token(str(other.public_id), user_id=other.id)

    created = await client.post(
        "/api/tools/data-extract/import",
        files={"file": ("owned.csv", BytesIO(CSV_SAMPLE.encode()), "text/csv")},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    batch_id = created.json()["batch_id"]

    denied = await client.get(
        f"/api/tools/data-extract/batches/{batch_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert denied.status_code == 403


@pytest.mark.asyncio
async def test_promote_pipe_embed_batch(auth_client: AsyncClient) -> None:
    created = await auth_client.post(
        "/api/tools/data-extract/import?profile=pipe_embed&format=delimited",
        files={"file": ("feed.pipe", BytesIO(PIPE_EMBED_LINE.encode()), "text/plain")},
    )
    assert created.status_code == 201
    batch_id = created.json()["batch_id"]

    promoted = await auth_client.post(
        f"/api/tools/data-extract/batches/{batch_id}/promote",
    )
    assert promoted.status_code == 200
    payload = promoted.json()
    assert payload["promoted"] == 1
    assert payload["skipped"] == 0
