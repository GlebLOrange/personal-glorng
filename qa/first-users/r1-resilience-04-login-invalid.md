# r1-resilience-04-login-invalid

- **step:** 04 — login with `not-an-email` + short password
- **observed:** Client keeps login disabled for malformed email. No inline alert like inquiry form (silent disable). Nav "login" click earlier only focused; needed direct `/login` navigation.
- **intended action:** Probe login invalid-input handling.
