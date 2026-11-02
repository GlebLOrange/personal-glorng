# Local Gortex Mermaid exports

**Not handbook docs.** System architecture for readers lives in [`docs/guide/architecture.md`](../guide/architecture.md) and the [architecture inventory](../generated/architecture-inventory.md).

Files in this directory are optional local dumps from the Gortex graph:

| File | Contents |
|------|----------|
| `architecture.mermaid` | Community coupling graph |
| `communities.mermaid` | Overlapping community graph (IDs/counts may differ) |
| `processes.mermaid` | Sample call-graph process subgraphs (large; incomplete vs full platform) |

## Regen

Local git hooks (installed by `gortex githook install`) run on post-commit / post-merge:

```bash
gortex export --format mermaid --scope all --out-dir docs/architecture/ --on-commit
```

Manual: same command from the repo root when the Gortex daemon has this repo tracked.

## Git / VitePress

- `*.mermaid` here are **gitignored** — regenerating after commits must not churn PRs.
- This folder is **excluded from VitePress** — do not embed `processes.mermaid` in the published site.
- Prefer live Gortex `analyze(operation:"communities")` or [`.cursor/references/gortex-communities.md`](../../.cursor/references/gortex-communities.md) for agents; community IDs in dumps drift and are not a stable contract.
