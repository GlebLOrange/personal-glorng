"""Format-specific extraction handlers."""

from app.core.data_extractor.handlers.csv_handler import extract_csv
from app.core.data_extractor.handlers.json_handler import extract_json
from app.core.data_extractor.handlers.xml_handler import extract_xml

__all__ = ["extract_csv", "extract_json", "extract_xml"]
