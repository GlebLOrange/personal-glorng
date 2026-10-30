# Gortex worktree and branch routing

On-demand detail (moved out of always-on `gortex-workflow` for token efficiency).

- The session/CWD selects the view. A session-discovered checkout (a linked worktree included) is an automatic overlay; do not `track` it. Only an explicit user request to track creates a dedicated logical graph.
- **Overall** means the selected overlay plus exactly one designated primary in its Git family, never a union of incompatible branches. Unique overlay/base matches keep normal relevance order; for a duplicate identity the overlay wins, and deletion/tombstone masks hide the base copy.
- Freshness `exact:false` = the requested view was not served. Every fallback is read-only. `require_exact:true` refuses substitution; `require_fresh:true` awaits filesystem state under RFC3339 `wait_deadline`, routed automatic checkouts only; else `fresh:false`.
- Select explicitly when CWD is not the target: `view:{kind:"worktree",checkout_id:"…"}` or `view:{kind:"git_ref",value:"refs/heads/release",graph_id:"…"}`. Inactive ref/commit views are immutable committed structural/source snapshots: no working-copy LSP, `search.text`, or edits. Approved coordinator-backed exact worktree edits are supported; fallback and ref/commit views are not.
- Untracking a non-primary dedicated worktree demotes it to automatic only if another ready primary survives. Before primary closure, family forget, or `set-primary`, preview the effects and obtain user confirmation.
