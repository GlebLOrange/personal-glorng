"""Tests for unified file data extraction."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from httpx import AsyncClient

from app.core.data_extractor import extract
from app.core.data_extractor.format import resolve_format, sniff_format
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
