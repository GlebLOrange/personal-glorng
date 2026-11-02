# r1-resilience-06-shortener-invalid

- **step:** 06 — URL shortener invalid URL + XSS-ish title; double-click shorten
- **observed:** Client enables shorten for `not a url!!!`. Button shows "creating…" then returns idle with fields kept. No visible validation/error message in UI. Script tag in title does not execute (good). Double-click protected by busy state.
- **intended action:** Public tool form invalid input + double-submit.
