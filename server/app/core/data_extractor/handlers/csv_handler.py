"""CSV file extraction."""

from __future__ import annotations

import csv
import io
from typing import Any

from app.core.data_extractor.types import ExtractOptions
from app.core.exceptions import ValidationError

HandlerResult = tuple[list[Any], dict[str, Any]]


def extract_csv(content: str, options: ExtractOptions) -> HandlerResult:
    if not content.strip():
        return [], {"row_count": 0, "columns": []}

    delimiter = options.csv_delimiter
    if delimiter is None and content.lstrip().startswith("\t"):
        delimiter = "\t"

    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter or ",")
    if reader.fieldnames is None:
        raise ValidationError("CSV file has no header row")

    records = [dict(row) for row in reader]
    columns = list(reader.fieldnames)
    return records, {"row_count": len(records), "columns": columns}
