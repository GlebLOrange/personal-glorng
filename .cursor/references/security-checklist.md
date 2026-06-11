# Security Review Checklist

Use during the Security axis of code review. For workflow guidance, see the `security-and-hardening` rule.

## OWASP Top 10 (2021) Quick Reference

| # | Category | Primary prevention |
|---|----------|-------------------|
| A01 | Broken Access Control | AuthZ on every endpoint; deny by default |
| A02 | Cryptographic Failures | TLS in transit; strong hashing at rest |
| A03 | Injection | Parameterized queries; validate/escape all input |
| A04 | Insecure Design | Threat model; least privilege; secure defaults |
| A05 | Security Misconfiguration | Harden headers, CORS, error handling |
| A06 | Vulnerable Components | Pin deps; audit (`npm audit`, `pip audit`) |
| A07 | Identification & Authentication Failures | Strong sessions; rate limit login; MFA where needed |
| A08 | Software & Data Integrity Failures | Verify CI/CD, webhooks, signed artifacts |
| A09 | Security Logging & Monitoring Failures | Log auth failures; alert on anomalies |
| A10 | Server-Side Request Forgery (SSRF) | Allowlist outbound URLs; block internal ranges |

## Secrets and Credentials

- [ ] No API keys, passwords, tokens, or private keys in source code
- [ ] No secrets in logs, error messages, or debug output
- [ ] `.env` and credential files excluded from version control
- [ ] Secrets loaded from environment variables or secure vaults
- [ ] Default/dev credentials are not used in production paths

**Red flags:** Hardcoded `sk_`, `AKIA`, `Bearer ` tokens, `password = "..."`, secrets in test fixtures committed to repo.

## Input Validation and Sanitization

- [ ] All user input validated at system boundaries (API, forms, CLI, webhooks)
- [ ] Type, length, format, and range constraints enforced
- [ ] Reject unexpected fields rather than silently ignoring them
- [ ] File uploads checked for type, size, and content
- [ ] Path traversal prevented in file/path parameters

**Red flags:** `request.body` used directly without validation, `eval()` on user input, unchecked `redirect` URLs.

## Authentication and Authorization

- [ ] Protected endpoints require authentication
- [ ] Authorization checked before sensitive operations (not just authentication)
- [ ] Principle of least privilege — roles/permissions are minimal
- [ ] Session/token expiry and revocation handled
- [ ] Admin or privileged actions have explicit guards

**Red flags:** Missing auth on new endpoints, checking role only in UI not API, trusting client-side role claims.

## Injection Prevention

- [ ] SQL queries use parameterized statements or ORM (no string concatenation)
- [ ] No shell command construction from user input without sanitization
- [ ] Template rendering escapes user content by default
- [ ] LDAP, XPath, and NoSQL queries parameterized where applicable

**Red flags:** `f"SELECT * FROM users WHERE id = {user_id}"`, `os.system(user_input)`, `innerHTML = userContent`.

## Output Encoding (XSS Prevention)

- [ ] HTML output escapes user-controlled data
- [ ] JavaScript context uses proper encoding (not just HTML escape)
- [ ] URL parameters encoded before insertion into links
- [ ] Content-Security-Policy considered for new UI surfaces
- [ ] `dangerouslySetInnerHTML` / `v-html` used only with sanitized content

**Red flags:** Unescaped user content in templates, reflected search terms in HTML, stored XSS in rich text fields.

## External and Untrusted Data

- [ ] API responses from third parties validated before use
- [ ] Webhook payloads verified (signatures, timestamps, replay protection)
- [ ] Config files from external sources treated as untrusted
- [ ] User-generated content sanitized before storage and rendering
- [ ] SSRF prevented when fetching user-supplied URLs

**Red flags:** Trusting `Host` header for redirects, fetching arbitrary URLs server-side, deserializing untrusted data.

## Dependencies

- [ ] New dependencies from trusted, maintained sources
- [ ] Known vulnerabilities checked (`npm audit`, `pip audit`, SCA tools)
- [ ] License compatible with project requirements
- [ ] Dependency version pinned or range constrained
- [ ] Existing stack considered before adding new package

**Red flags:** Unmaintained packages (years since last commit), copy-pasted code from unknown sources, unnecessary dependency for one-liner utility.

## Pre-Commit Verification

### Authentication

- [ ] Passwords hashed with bcrypt/scrypt/argon2 (salt rounds ≥ 12)
- [ ] Session tokens are httpOnly, secure, sameSite
- [ ] Login has rate limiting
- [ ] Password reset tokens expire

### Authorization

- [ ] Every endpoint checks user permissions
- [ ] Users can only access their own resources
- [ ] Admin actions require admin role verification

### Input

- [ ] All user input validated at the boundary
- [ ] SQL queries are parameterized
- [ ] HTML output is encoded/escaped
- [ ] Server-side URL fetches are allowlisted (no SSRF to internal services)

### Data

- [ ] No secrets in code or version control
- [ ] Sensitive fields excluded from API responses
- [ ] PII encrypted at rest (if applicable)

### Infrastructure

- [ ] Security headers configured (CSP, HSTS, etc.)
- [ ] CORS restricted to known origins
- [ ] Dependencies audited for vulnerabilities
- [ ] Error messages don't expose internals

### Supply Chain

- [ ] Lockfile committed; CI installs with `npm ci`
- [ ] New dependencies reviewed (maintenance, downloads, postinstall scripts)

### AI / LLM (if used)

- [ ] Model output treated as untrusted (no eval/SQL/innerHTML/shell)
- [ ] Secrets and other users' data kept out of prompts
- [ ] Tool/agent permissions scoped; destructive actions require confirmation

## Severity Guide

| Finding | Severity |
|---------|----------|
| Exposed secrets, SQL injection, auth bypass | **Critical** — blocks merge |
| Missing input validation on sensitive endpoint | Required — must fix |
| Missing rate limiting on new public endpoint | **Optional** — suggest |
| CSP header not updated for new inline script | **Consider** — evaluate risk |
