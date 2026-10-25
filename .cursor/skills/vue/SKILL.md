---
name: vue
description: Vue 3 Composition API, TypeScript, Pinia auth session, composables, and Vitest for the Vite client
---

# Vue 3 client

## Core principles

- Use Vue 3 Composition API with `<script setup lang="ts">`.
- Do not add Options API, mixins, or `this`-based component code.
- Write strict TypeScript and avoid `any`.
- Prefer composables for reusable reactive logic.
- Keep templates readable; move complex logic into `computed` values, composables, or small helpers.
- Keep changes small and local to the task. Prefer clear names, early returns, and existing composables, stores, utilities, and components.

## Component rules

- Use `defineProps<T>()` with TypeScript generics for props.
- Use typed `defineEmits<T>()` for emitted events.
- Use `defineModel()` for new v-model bindings when it keeps the component simpler.
- Keep one component per file; component filenames should stay PascalCase.
- Name template/child event handlers clearly: prefer `handle*` **or** a clear verb (`openCreate`, `runIngest`, `setStatusFilter`). Stay consistent within a file.
- Move complex template expressions into `computed` values or small helpers.
- `BaseInput` / `BaseSelect` / `BaseTextarea` default to `labelAlign: "end"` (accessible name via sr-only; no visible trailing field name). Do not set `label-align="start"` (border notch) on expense or other forms.

## Composables

- Prefix reusable composables with `use`.
- Return explicit loading/error state for async composables when the UI depends on it.
- Place shared composables under `client/src/composables`.
- Use the existing API layer (`useApi`, `useCachedApi`) for data fetching.

## TypeScript

- Prefer `type` for local aliases and `interface` for shared object contracts that are extended.
- Use `satisfies` when it improves checking without widening types.
- Avoid type assertions unless the value has already been validated or narrowed.
- Prefer `const`; use `let` only when reassignment is needed.
- Use `unknown` at external boundaries and narrow it. Treat API responses, persisted store data, URL params, and browser state as untrusted until validated.

## Pinia — state ownership

Canonical store: `client/src/stores/auth.ts`. Prefer that file over inventing new store shapes.

- Keep component-only state in the component with `ref`, `reactive`, or `computed`.
- Use Pinia for shared client session / UI workflow that spans routes, layouts, or unrelated trees.
- Prefer composables for feature state (weather, guest prefs, cached API reads).
- Use route params and query strings for shareable navigation state.
- Keep server state in the API/composable layer unless Pinia intentionally owns UI workflow state.
- Do not copy list/detail fetch caches into Pinia unless it is an intentional editable draft, offline cache, or workflow snapshot.

## Pinia — store structure

- Prefer setup stores with `defineStore('name', () => { ... })`.
- Use `storeToRefs()` when destructuring store state or getters.
- One store file per domain under `client/src/stores/`. Today that is only `auth`; do not grow a second god store.
- Keep state, computed getters, and actions together when they represent one cohesive domain.
- Return every state property from setup stores so Pinia can track it for devtools and plugins.
- Keep getters pure and side-effect free; put writes, I/O, and orchestration in actions.

```ts
import { computed, ref } from "vue";
import { defineStore } from "pinia";

import type { UserResponse } from "@/types";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<UserResponse | null>(null);
  const sessionResolved = ref(false);
  const sessionError = ref<string | null>(null);

  const isAuthenticated = computed(() => !!user.value);

  async function resolveSession(): Promise<void> {
    // Restore cookie session; see client/src/stores/auth.ts for full flow.
  }

  return {
    user,
    sessionResolved,
    sessionError,
    isAuthenticated,
    resolveSession,
  };
});
```

## Pinia — component usage

- Call stores at the top of `<script setup>` or inside setup functions, getters, and actions.
- Destructure actions directly when useful; actions remain bound to the store.
- Avoid writing large business workflows in components; move them to store actions or composables.
- Prefer computed values over watchers when deriving state.

```vue
<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const { sessionError } = storeToRefs(auth);
const { logout } = auth;
</script>
```

## Session and side effects

- Auth is cookie-based. Never store access tokens, refresh tokens, or authorization decisions in Pinia or browser storage.
- Bootstrap: `main.ts` mounts the app, then `restoreAuth()` (`client/src/plugins/auth.ts`) calls `resolveSession` after the router is ready.
- `resolveSession` / `sessionResolved` / `sessionError`: keep the prior user on non-401 failures (avoid bounce on network/5xx blips); clear the user only after confirmed auth failure.
- Deduplicate concurrent session restore with an in-flight promise (see `resolveInFlight` in the auth store).
- Use dynamic `import()` inside actions when needed to break circular dependencies (e.g. firebase sign-in, guest weather sync after login).
- Validate action inputs at the boundary before mutating store state.
- Keep subscriptions, intervals, sockets, and browser listeners outside stores unless the store owns their lifecycle and cleanup.

## Router guards and browser state

- Use stores inside setup, getters, actions, or router guards where the active Pinia instance is available (`client/src/router/index.ts`).
- Do not read browser-only storage during module initialization in store files.
- Avoid singleton state that can outlive the current app instance in tests or previews.

## Persistence

- Do not add `pinia-plugin-persistedstate` or other Pinia persist plugins.
- Guest/local prefs and locations: use existing composables (`useLocalStorage`, weather location helpers), not Pinia.
- Authenticated preferences: API via store actions (`fetchPreferences` / `updatePreferences`) or composables that call the auth store.
- Treat any browser-stored values as untrusted input; validate before use in critical workflows.

## Testing

- Use Vitest and `@vue/test-utils`.
- Keep component tests behavior-focused.
- Prefer `mount()` unless a shallow render is clearly enough.
- Primary Pinia pattern: `setActivePinia(createPinia())` in `beforeEach`; mock `@/composables/useApi`; test store actions directly (see `client/src/stores/auth.test.ts`).
- Reset Pinia between tests to avoid shared state leakage.
- `@pinia/testing` / `createTestingPinia` is optional for heavy component stubs only — do not install it unless a test clearly needs store stubs.

## Tailwind CSS

- Use existing utility classes and design tokens.
- Extract repeated UI patterns to components before adding ad hoc CSS.
- Respect dark mode and reduced motion patterns already in the client.

## Safety

- Never use raw `v-html`; only use sanitized HTML through existing utilities.
- Use safe URL/image helpers for dynamic navigation or media sources.
- Do not mutate props. Do not use `var`.

## Pinia anti-patterns

- Do not use Pinia as a dumping ground for every reactive value.
- Do not destructure state directly from a store without `storeToRefs()`.
- Do not put server-only objects, request instances, DOM nodes, or timers in store state.
- Do not grow a second god store; prefer a composable when state is feature-scoped.
- Do not read `localStorage` at module top-level in store files.

## Verification

- Prefer focused Vitest files, `npm run typecheck`, or `npm run lint` for touched client code.
- Run Playwright only when the user asks, CI is failing, or the change affects a critical browser flow.
