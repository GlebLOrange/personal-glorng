# Frontend harness notes

**Entry:** `client/` — Vue 3 + Vite + TypeScript.

**Standards:** `.cursor/skills/vue-client/SKILL.md`, `.cursor/skills/vue-pinia/SKILL.md`, `.cursor/rules/vue-client.mdc`

**Checks:**

```bash
cd client
npm ci
npm run lint && npm run format:check && npm run test:coverage && npm run build:check
```

For UI-only tweaks, `npm run lint` + relevant Vitest files may suffice during iteration.
