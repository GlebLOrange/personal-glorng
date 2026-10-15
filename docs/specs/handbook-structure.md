# Spec: Handbook information architecture

## Objective

A reader (contributor, operator, or recruiter on the published handbook) should find setup, the system picture, and day-to-day commands in one place each. Success is less duplication and no stale “do this next” instructions, not a new information architecture.

## Assumptions

- Documentation-only. No application code, Makefile, or skill-body changes.
- The published GitHub Pages site stays the full handbook, including operations.
- Agent files stay dispatch tables. [`AGENTS.md`](../../AGENTS.md) and [`CODING_STANDARDS.md`](../../CODING_STANDARDS.md) point at skills; the handbook only links them.
- Approach: tighten in place (keep Guide / Operations / Reference / ADRs). No Diátaxis reshuffle and no unpublishing operations.

## Ownership (one page per fact)

| Fact | Owner |
|------|--------|
| First-run recipe and minimum secrets | [Getting started](/guide/getting-started) |
| Dev modes and command catalog | [Development](/guide/development) |
| Traffic flow, channels, data stores, request pipeline | [Architecture](/guide/architecture) |
| Service catalog, pillars, terminology | [Platform overview](/reference/platform) |
| Branch / PR workflow and “who owns what” | [Contributing](/guide/contributing) |
| Door (what this is, links, one command line) | [README](../../README.md) |
| Agent entry / skill index | [`AGENTS.md`](../../AGENTS.md), [`CODING_STANDARDS.md`](../../CODING_STANDARDS.md) |

## Commands

```bash
make docs-build   # docs-generate + VitePress build
make docs-dev     # http://localhost:5173
```

Do not regenerate catalogs unless a page change depends on `scripts/generate_docs.py`.

## Project structure

```
README.md                 Door — links into the handbook
docs/                     VitePress handbook
docs/guide/               Setup, architecture, development, frontend, contributing
docs/operations/          Deployment, database, backups, Cloudflare, Cloud VM
docs/reference/           Platform, API, config, security, testing
docs/adr/                 Architecture decision records
docs/specs/               Feature and program specs (this file)
docs/generated/           OpenAPI + architecture inventory (generated)
AGENTS.md                 Agent entry map (dispatch only)
CODING_STANDARDS.md       Skill index (pointer table)
```

## Docs style

Short sections, copy-paste command blocks, VitePress links like `/guide/development`, repo-relative links for files outside the site. Do not add a separate style-guide page.

## Testing strategy

- Check: `make docs-build` (dead-link checking on for handbook routes; localhost and repo-relative `../../` source links allowlisted).
- Manual: open the docs preview and click home, getting started, architecture, platform, and specs.
- No new test framework.

## Boundaries

- **Always:** one owner per fact; update the existing page; verify a command against the Makefile before writing it; keep generated files generated.
- **Ask first:** moving ops pages off the public site; generating configuration from `.env.example`; editing skill bodies; adding a dependency.
- **Never:** invent commands or env vars; commit secrets; paste skill text into the handbook; rewrite deployment or security in this program unless scoped separately.

## Success criteria

- README links to Getting started for first-run setup and does not repeat the full first-run recipe.
- The channel table exists only in Architecture.
- Every hand-written page under `docs/` is in the sidebar, or is generated (`docs/generated/`).
- Getting started and the P3 roadmap no longer instruct a finished step.
- `make docs-build` passes with dead-link checking on (handbook routes; localhost and `../../` source links allowlisted).
- `AGENTS.md` and `CODING_STANDARDS.md` stay pointer tables.

## Out of scope

Deployment, Cloudflare, backup, security, configuration env reference, and generated OpenAPI / architecture inventory rewrites.
