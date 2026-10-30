---
name: gortex-routers-tools-10-dirs
description: "Work in the routers/tools +10 dirs area — 132 symbols across 26 files (76% cohesion)"
---

# routers/tools +10 dirs

132 symbols | 26 files | 76% cohesion

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
- `server/app/services/password_generator.py`
- `server/app/services/weather_location.py`
- `server/app/services/webhooks.py`
- `server/tests/test_currency_parity.py`
- `server/tests/test_data_extractor.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | SystemRandom, isnan, choice, secrets, collections.Counter, ... |
| `external-call::dep:app.core.data_extractor.registry.HANDLERS` | app.core.data_extractor.registry.HANDLERS |
| `server/app/core/catalogs.py` | _load_expense_catalog |
| `server/app/core/data_extractor/__init__.py` | source, extract, options, source, _load_content, ... |
| `server/app/core/data_extractor/format.py` | resolve_format, format, parse_format, filename, sniff_format, ... |
| `server/app/core/data_extractor/handlers/csv_handler.py` | content, options, extract_csv |
| `server/app/core/data_extractor/handlers/json_handler.py` | _normalize_json, parsed, extract_json, content, options |
| `server/app/core/data_extractor/handlers/xml_handler.py` | element, tag, content, _element_to_tree, _local_name, ... |
| `server/app/core/data_extractor/profiles/__init__.py` | known_profiles, options, apply_profile, profile |
| `server/app/core/data_extractor/types.py` | ExtractOptions, DataFormat |
| `server/app/core/date_ranges.py` | month, month_date_bounds |
| `server/app/core/exceptions.py` | message, ValidationError, __init__ |
| `server/app/db/documents/weather.py` | WeatherLocation |
| `server/app/db/seed/core/recipes.py` | load_sample_recipes |
| `server/app/routers/tools/calculator.py` | b, op, a, calculate, data, ... |
| `server/app/routers/tools/data_extract.py` | field_delimiter, raw, profile, field_names, row_tag, ... |
| `server/app/routers/tools/password_generator.py` | data, generate |
| `server/app/routers/tools/tasks_admin.py` | data, _resolve_telegram_user_id, settings |
| `server/app/schemas/calculator.py` | CalculatorRequest, CalculatorResponse |
| `server/app/schemas/password_generator.py` | PasswordGeneratorRequest, PasswordGeneratorResponse |
| `server/app/services/data_extract.py` | format, options, row_tag, list_delimiter, contents, ... |
| `server/app/services/password_generator.py` | lowercase, uppercase, digits, generate_password, exclude_ambiguous, ... |
| `server/app/services/weather_location.py` | ordered_ids, user_id, list_locations, registry, user_id, ... |
| `server/app/services/webhooks.py` | body, parse_webhook_json |
| `server/tests/test_currency_parity.py` | test_expense_catalog_matches_shared_fixture |
| `server/tests/test_data_extractor.py` | test_extract_csv_from_path, test_sniff_format_from_extension, test_extract_json_scalar_list, test_extract_json_array, test_extract_json_object, ... |

## Connected Communities

- **app/services +15 dirs** (12 cross-edges)
- **app/services +12 dirs** (7 cross-edges)
- **app/services +7 dirs · lower** (4 cross-edges)
- **tests +10 dirs** (3 cross-edges)
- **. +8 dirs · app.core.logging.logger** (2 cross-edges)
- **data_extractor/handlers** (2 cross-edges)
- **. +8 dirs · ingest** (2 cross-edges)
- **tests +4 dirs** (1 cross-edges)
- **. +3 dirs · list_expenses** (1 cross-edges)
- **app/services +11 dirs · ApiError** (1 cross-edges)
- **. +2 dirs · transform_pipe_embed_record** (1 cross-edges)
- **. +2 dirs · custom_openapi** (1 cross-edges)
- **tests +9 dirs** (1 cross-edges)
- **. +2 dirs · fetch_multicooker_candidates** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-377")
explore(operation:"context", task:"understand routers/tools +10 dirs", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
