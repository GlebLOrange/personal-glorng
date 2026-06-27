"""Small XML safety checks for stdlib parsers."""

_UNSAFE_XML_MARKERS = ("<!doctype", "<!entity")


def has_unsafe_xml_declaration(content: str) -> bool:
    """Return True when XML declares DTDs or entities."""
    lowered = content[:4096].lower()
    return any(marker in lowered for marker in _UNSAFE_XML_MARKERS)
