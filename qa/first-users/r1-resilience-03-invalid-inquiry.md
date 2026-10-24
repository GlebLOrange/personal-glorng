# r1-resilience-03-invalid-inquiry

- **step:** 03 — invalid email + short message; double-click send
- **observed:** Email `not-an-email` marks invalid with alert "use a full address like name@example.com". Send stays disabled; double-click on disabled send is blocked (cannot interact). No crash/error page.
- **intended action:** Probe validation and double-submit resilience without sending mail.
