# r2-resilience-07-login-invalid-attempt

- Action: Double-click Login with `qa+bad@example.test` / wrong password
- Observation: Button showed “signing in…” (busy/disabled) — no double-submit UI. Error: `.test` rejected as reserved/special-use domain by server email validator.
