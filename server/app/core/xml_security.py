"""XML safety helpers backed by defusedxml."""

from __future__ import annotations

from xml.etree.ElementTree import Element

from defusedxml import ElementTree as DefusedET
from defusedxml.common import DefusedXmlException

_UNSAFE_XML_MARKERS = ("<!doctype", "<!entity")


def has_unsafe_xml_declaration(content: str) -> bool:
    """Return True when XML declares DTDs or entities (fast pre-check)."""
    lowered = content[:4096].lower()
    return any(marker in lowered for marker in _UNSAFE_XML_MARKERS)


def parse_xml(content: str) -> Element:
    """Parse XML with defusedxml (rejects DTD/entity expansion)."""
    return DefusedET.fromstring(content)


__all__ = [
    "DefusedXmlException",
    "has_unsafe_xml_declaration",
    "parse_xml",
]
