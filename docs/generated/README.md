# Generated documentation

Files in this directory are produced by [`scripts/generate_docs.py`](../../scripts/generate_docs.py).

```bash
make docs-generate
```

Do not edit these files by hand. CI fails if they drift from the generators.

| File | Source |
|------|--------|
| `openapi.json` | FastAPI `create_app().openapi()` (also copied to `docs/public/openapi.json`) |
| `api-endpoints.md` | OpenAPI paths table |
| `architecture-inventory.md` | `PLATFORM_SERVICES` + Compose service names |
