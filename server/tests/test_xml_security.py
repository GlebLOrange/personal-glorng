"""Tests for defusedxml-backed XML helpers."""

from __future__ import annotations

import pytest

from app.core.xml_security import (
    DefusedXmlException,
    has_unsafe_xml_declaration,
    parse_xml,
)

_XXE = (
    "<?xml version='1.0'?>"
    "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>"
    "<foo>&xxe;</foo>"
)
_BILLION_LAUGHS = (
    "<?xml version='1.0'?>"
    "<!DOCTYPE lolz [<!ENTITY lol 'lol'>"
    "<!ENTITY lol2 '&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;'>]>"
    "<lolz>&lol2;</lolz>"
)


@pytest.mark.parametrize("payload", [_XXE, _BILLION_LAUGHS])
def test_parse_xml_rejects_entities_without_precheck(payload: str) -> None:
    with pytest.raises(DefusedXmlException):
        parse_xml(payload)


@pytest.mark.parametrize("payload", [_XXE, _BILLION_LAUGHS])
def test_precheck_flags_entity_declarations(payload: str) -> None:
    assert has_unsafe_xml_declaration(payload)


def test_parse_xml_accepts_plain_xml() -> None:
    xml = "<root><item id='1'>a</item><item id='2'>b</item></root>"
    assert not has_unsafe_xml_declaration(xml)
    root = parse_xml(xml)
    assert [(c.get("id"), c.text) for c in root] == [("1", "a"), ("2", "b")]
