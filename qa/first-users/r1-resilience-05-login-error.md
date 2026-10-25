# r1-resilience-05-login-error

- **step:** 05 — double-click login with qa+bad@example.test
- **observed:** Button goes to "signing in…" (disabled/busy) — double-click does not fire duplicate submits visibly. API returns: reserved `.test` TLD rejected ("special-use or reserved name"). Form stays usable; no crash.
- **intended action:** Bad credentials / reserved domain + double-submit resilience.
