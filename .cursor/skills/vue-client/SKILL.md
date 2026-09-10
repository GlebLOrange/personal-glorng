---
name: vue-client
description: Vue 3 component and TypeScript guidance for the Vite client.
---
# Vue 3 Client

## Core Principles
- Use Vue 3 Composition API with `<script setup lang="ts">`.
- Do not add Options API, mixins, or `this`-based component code.
- Write strict TypeScript and avoid `any`.
- Prefer composables for reusable reactive logic.
- Keep templates readable; move complex logic into `computed` values, composables, or small helpers.
- Keep changes small and local to the task. Prefer clear names, early returns, and existing composables, stores, utilities, and components.

## Component Rules
- Use `defineProps<T>()` with TypeScript generics for props.
- Use typed `defineEmits<T>()` for emitted events.
- Use `defineModel()` for new v-model bindings when it keeps the component simpler.
- Keep one component per file; component filenames should stay PascalCase.
- Name template/child event handlers clearly: prefer `handle*` **or** a clear verb (`openCreate`, `runIngest`, `setStatusFilter`). Stay consistent within a file.
- Move complex template expressions into `computed` values or small helpers.

## State Management (Pinia)
- Use setup stores with `defineStore('name', () => { ... })`.
- Use `storeToRefs()` when destructuring store state or getters.
- Keep stores focused by domain.
- Keep server state in the API/composable layer unless Pinia intentionally owns UI workflow state.
- For store ownership, session/auth, persistence, and testing detail, follow the `vue-pinia` skill (`.cursor/skills/vue-pinia/SKILL.md`).

## Composables
- Prefix reusable composables with `use`.
- Return explicit loading/error state for async composables when the UI depends on it.
- Place shared composables under `client/src/composables`.
- Use the existing API layer for data fetching.

## TypeScript
- Prefer `type` for local aliases and `interface` for shared object contracts that are extended.
- Use `satisfies` when it improves checking without widening types.
- Avoid type assertions unless the value has already been validated or narrowed.
- Prefer `const`; use `let` only when reassignment is needed.
- Use `unknown` at external boundaries and narrow it. Treat API responses, persisted store data, URL params, and browser state as untrusted until validated.

## Testing
- Use Vitest and `@vue/test-utils`.
- Keep component tests behavior-focused.
- Prefer `mount()` unless a shallow render is clearly enough.

## Tailwind CSS
- Use existing utility classes and design tokens.
- Extract repeated UI patterns to components before adding ad hoc CSS.
- Respect dark mode and reduced motion patterns already in the client.

## Safety
- Never use raw `v-html`; only use sanitized HTML through existing utilities.
- Use safe URL/image helpers for dynamic navigation or media sources.
- Do not mutate props. Do not use `var`.

## Verification
- Prefer focused Vitest files, `npm run typecheck`, or `npm run lint` for touched client code.
- Run Playwright only when the user asks, CI is failing, or the change affects a critical browser flow.
