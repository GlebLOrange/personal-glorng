"""XML file extraction."""

from __future__ import annotations

from collections import Counter
from typing import Any
from xml.etree.ElementTree import Element, ParseError

from defusedxml.common import DefusedXmlException

from app.core.data_extractor.types import ExtractOptions
from app.core.exceptions import ValidationError
from app.core.xml_security import has_unsafe_xml_declaration, parse_xml

HandlerResult = tuple[list[Any], dict[str, Any]]


def extract_xml(content: str, options: ExtractOptions) -> HandlerResult:
    if not content.strip():
        raise ValidationError("XML file is empty")
    if has_unsafe_xml_declaration(content):
        raise ValidationError("XML DTD and entity declarations are not supported")

    try:
        root = parse_xml(content)
    except (ParseError, DefusedXmlException, ValueError) as exc:
        raise ValidationError(f"Invalid XML: {exc}") from exc

    root_tag = _local_name(root.tag)
    if options.xml_mode == "tree":
        tree = _element_to_tree(root)
        return [tree], {
            "row_count": 1,
            "root_tag": root_tag,
            "xml_mode": "tree",
        }

    row_tag = options.row_tag or _detect_row_tag(root)
    rows = [
        _element_to_row(child) for child in root if _local_name(child.tag) == row_tag
    ]
    if not rows and options.row_tag:
        raise ValidationError(f"No XML elements found with tag '{options.row_tag}'")

    columns = _collect_columns(rows)
    meta: dict[str, Any] = {
        "row_count": len(rows),
        "root_tag": root_tag,
        "row_tag": row_tag,
        "xml_mode": "rows",
    }
    if columns:
        meta["columns"] = columns
    return rows, meta


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", maxsplit=1)[-1]
    return tag


def _detect_row_tag(root: Element) -> str:
    counts = Counter(_local_name(child.tag) for child in root)
    if not counts:
        raise ValidationError("XML root has no child elements for row extraction")
    row_tag, count = counts.most_common(1)[0]
    if count < 1:
        raise ValidationError("Could not detect repeated XML row tag")
    return row_tag


def _element_text(element: Element) -> str | None:
    text = (element.text or "").strip()
    return text or None


def _element_to_row(element: Element) -> dict[str, Any]:
    row: dict[str, Any] = dict(element.attrib)
    text = _element_text(element)
    if text is not None:
        row["#text"] = text

    for child in element:
        key = _local_name(child.tag)
        value = _child_value(child)
        if key in row:
            existing = row[key]
            if isinstance(existing, list):
                existing.append(value)
            else:
                row[key] = [existing, value]
        else:
            row[key] = value
    return row


def _child_value(element: Element) -> object:
    if len(element):
        return _element_to_tree(element)
    text = _element_text(element)
    if element.attrib:
        payload = dict(element.attrib)
        if text is not None:
            payload["#text"] = text
        return payload
    return text


def _element_to_tree(element: Element) -> dict[str, Any]:
    node: dict[str, Any] = dict(element.attrib)
    text = _element_text(element)
    if text is not None:
        node["#text"] = text

    for child in element:
        key = _local_name(child.tag)
        value = _element_to_tree(child)
        if key in node:
            existing = node[key]
            if isinstance(existing, list):
                existing.append(value)
            else:
                node[key] = [existing, value]
        else:
            node[key] = value
    tag = _local_name(element.tag)
    if not node and text is None:
        return {tag: None}
    return {tag: node}


def _collect_columns(rows: list[dict[str, Any]]) -> list[str]:
    columns: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                columns.append(key)
    return columns
