# Groq prompt-caching work

Load this reference only for tasks about prompt caching, AI usage measurement, or the Groq-backed chat and task-intake flows. Treat `plan-gpt.md` as a proposal and verify current code, settings, provider behavior, and pricing before relying on its findings.

## Guardrails

- Keep the initial optimization on the existing Groq integration and model. Do not add OpenAI-only request parameters to Groq calls, change providers or models, or deploy without separate user approval.
- Complete the baseline audit before changing production prompts or behavior. The audit is read-only; report findings and proposed changes separately.
- Separate observed measurements, estimates, assumptions, and unknowns. Do not claim cache savings without provider usage evidence. Missing usage is unknown, never zero.
- Verify current Groq caching eligibility, endpoint behavior, minimum-prefix requirements, cache lifetime, and exact-model pricing before drawing conclusions or calculating costs.
- Log structured metadata only. Never log prompts, user task contents, model responses, secrets, or API keys.
- Keep provider attempts and retries distinguishable from logical user requests; do not double-count retries in request-level aggregates.

## Phases and gates

### 0. Read-only baseline audit

Identify every production AI request path and caller of the shared JSON completion helper. Trace frontend conversation-history construction and ordering; backend prompt and payload construction; effective model, endpoint, and feature flags; available logs and retention; cached-token usage availability; and retry behavior. Verify provider documentation and pricing for the live configuration.

**Deliverable:** a concise inventory of request paths, history behavior, available and missing metrics, retry semantics, and verified provider assumptions. Do not modify application code or prompts in this phase.

**Gate:** proceed to implementation only after the baseline is documented and the user requests implementation. If usage evidence or provider facts are unavailable, mark them unknown rather than infer a baseline.

### 1. Prompt and payload stability

Keep stable system prompts first and unchanged across equivalent requests; keep request-specific data out of stable prefixes where practical; preserve message ordering; and serialize equivalent task-intake payloads consistently. Make changes only after checking schema compatibility and existing tests.

**Acceptance:** identical logical payloads serialize identically; extraction schemas, clarification behavior, scheduling, and public contracts remain unchanged; stable system-first ordering is preserved.

### 2. Usage observability

Where provider usage permits, record feature, model, input/prompt, cached-input, uncached-input, completion tokens, latency, usage availability, and attempt/retry metadata. Calculate token-weighted cache rate as cached input divided by eligible input tokens, and request-weighted rate as eligible requests with cached input divided by eligible requests with valid usage. Label cost as an estimate based on verified pricing.

**Acceptance:** chat and task-intake expose consistent metadata where available; unknown usage stays distinct from zero; retries do not inflate logical-request totals; streaming and non-streaming behavior are measured separately when their usage differs; no sensitive content is logged.

### 3. Repeatable cache evaluation

Extend the existing evaluation approach with repeated identical requests and controlled changes to task text, clarification history, date, and system prompt. Distinguish cold and warm runs where measurable; record model, endpoint, timestamp, repetitions, usage availability, cached and uncached tokens, latency, estimated cost, and extraction correctness. Account for provider cache expiration and minimum-prefix requirements.

**Gate:** cache effectiveness and prompt quality are separate evaluations. Do not change production prompts until repeatable results and regression tests support the change; one warm hit is not proof of consistent savings.

### 4. Usage reporting

Start with existing structured logs and aggregation. Compare cache rates, estimated cost, token totals, latency, and unavailable-usage counts by feature and model. Add a database or new analytics infrastructure only when the existing approach is shown to be insufficient.

### 5. Optional provider research

Only when separately requested, compare OpenAI-compatible alternatives using current documentation, measured workloads, pricing, retention, structured outputs, tools, streaming, and migration cost. Keep provider-specific request behavior isolated. Do not migrate providers or introduce an abstraction without a demonstrated operational or financial case and separate approval.

## Validation

Cover provider usage parsing, cached-token calculations, unknown-versus-zero handling, current-price cost estimates, deterministic serialization, stable request structure and system-first ordering, streaming and JSON usage parsing, retry accounting, extraction correctness, clarification behavior, and existing chat/task behavior. Keep cache metrics separate from quality results. Before any deployment, obtain explicit approval and report measured results separately from estimates and assumptions.
