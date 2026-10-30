---
name: gortex-app-services-10-dirs-validationerror
description: "Work in the app/services +10 dirs · ValidationError area — 135 symbols across 27 files (76% cohesion)"
---

# app/services +10 dirs · ValidationError

135 symbols | 27 files | 76% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `external-call::dep:app.core.data_extractor.registry.HANDLERS`
- `server/app/core/catalogs.py`
- `server/app/core/data_extractor/__init__.py`
- `server/app/core/data_extractor/format.py`
- `server/app/core/data_extractor/handlers/csv_handler.py`
- `server/app/core/data_extractor/handlers/json_handler.py`
- `server/app/core/data_extractor/handlers/xml_handler.py`
- `server/app/core/data_extractor/profiles/__init__.py`
- `server/app/core/data_extractor/types.py`
- `server/app/core/date_ranges.py`
- `server/app/core/exceptions.py`
- `server/app/db/documents/weather.py`
- `server/app/db/seed/core/recipes.py`
- `server/app/routers/tools/calculator.py`
- `server/app/routers/tools/data_extract.py`
- `server/app/routers/tools/password_generator.py`
- `server/app/routers/tools/tasks_admin.py`
- `server/app/schemas/calculator.py`
- `server/app/schemas/password_generator.py`
- `server/app/services/data_extract.py`
- `server/app/services/news.py`
- `server/app/services/password_generator.py`
- `server/app/services/weather_location.py`
- `server/app/services/webhooks.py`
- `server/tests/test_currency_parity.py`
- `server/tests/test_data_extractor.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | math, secrets, shuffle, isinf, calendar.monthrange, ... |
| `external-call::dep:app.core.data_extractor.registry.HANDLERS` | app.core.data_extractor.registry.HANDLERS |
| `server/app/core/catalogs.py` | _load_expense_catalog |
| `server/app/core/data_extractor/__init__.py` | filename, filename, source, options, format, ... |
| `server/app/core/data_extractor/format.py` | filename, sniff_format, value, resolve_format, format, ... |
| `server/app/core/data_extractor/handlers/csv_handler.py` | content, extract_csv, options |
| `server/app/core/data_extractor/handlers/json_handler.py` | options, extract_json, _normalize_json, content, parsed |
| `server/app/core/data_extractor/handlers/xml_handler.py` | _element_to_tree, element, extract_xml, options, content, ... |
| `server/app/core/data_extractor/profiles/__init__.py` | known_profiles, apply_profile, profile, options |
| `server/app/core/data_extractor/types.py` | DataFormat, ExtractOptions |
| `server/app/core/date_ranges.py` | month_date_bounds, month |
| `server/app/core/exceptions.py` | __init__, ValidationError, message |
| `server/app/db/documents/weather.py` | WeatherLocation |
| `server/app/db/seed/core/recipes.py` | load_sample_recipes |
| `server/app/routers/tools/calculator.py` | op, a, _evaluate, b, data, ... |
| `server/app/routers/tools/data_extract.py` | raw, row_tag, list_delimiter, field_delimiter, _parse_field_names, ... |
| `server/app/routers/tools/password_generator.py` | data, generate |
| `server/app/routers/tools/tasks_admin.py` | data, settings, _resolve_telegram_user_id |
| `server/app/schemas/calculator.py` | CalculatorRequest, CalculatorResponse |
| `server/app/schemas/password_generator.py` | PasswordGeneratorRequest, PasswordGeneratorResponse |
| `server/app/services/data_extract.py` | xml_mode, filename, options, profile, contents, ... |
| `server/app/services/news.py` | data, _article_source_fields, source |
| `server/app/services/password_generator.py` | length, digits, symbols, lowercase, exclude_ambiguous, ... |
| `server/app/services/weather_location.py` | list_locations, registry, user_id, user_id, user_id, ... |
| `server/app/services/webhooks.py` | body, parse_webhook_json |
| `server/tests/test_currency_parity.py` | test_expense_catalog_matches_shared_fixture |
| `server/tests/test_data_extractor.py` | test_extract_xml_rows_auto_detect, test_extract_delimited_skips_bad_line_with_profile, test_sniff_format_from_extension, test_extract_xml_missing_row_tag, test_extract_xml_tree_mode, ... |

## Connected Communities

- **app/services +15 dirs** (12 cross-edges)
- **app/services +12 dirs** (7 cross-edges)
- **app/services +7 dirs · lower** (4 cross-edges)
- **tests +10 dirs** (3 cross-edges)
- **. +8 dirs · ingest** (2 cross-edges)
- **data_extractor/handlers** (2 cross-edges)
- **. +8 dirs · app.core.logging.logger** (2 cross-edges)
- **tests +4 dirs** (1 cross-edges)
- **. +2 dirs · transform_pipe_embed_record** (1 cross-edges)
- **. +2 dirs · custom_openapi** (1 cross-edges)
- **. +3 dirs · list_expenses** (1 cross-edges)
- **. +2 dirs · fetch_multicooker_candidates** (1 cross-edges)
- **app/services +11 dirs · ApiError** (1 cross-edges)
- **tests +9 dirs** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-378")
explore(operation:"context", task:"understand app/services +10 dirs · ValidationError", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
