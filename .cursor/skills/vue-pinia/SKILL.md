---
name: vue-pinia
description: Vue 3 Pinia guidance for this client — auth session store, composables vs stores, cookie auth, and Vitest with createPinia.
---
You are an expert in Vue 3, TypeScript, and Pinia state management for this portfolio client (Pinia ^4).

# Vue + Pinia Guidelines

Canonical store: `client/src/stores/auth.ts`. Prefer that file over inventing new store shapes.

## State Ownership
- Keep component-only state in the component with `ref`, `reactive`, or `computed`.
- Use Pinia for shared client session / UI workflow that spans routes, layouts, or unrelated trees.
- Prefer composables for feature state (weather, guest prefs, cached API reads). Place them under `client/src/composables`.
- Use route params and query strings for shareable navigation state.
- Use the existing API layer (`useApi`, `useCachedApi`) for server state.
- Do not copy list/detail fetch caches into Pinia unless it is an intentional editable draft, offline cache, or workflow snapshot.

## Store Structure
- Prefer setup stores with `defineStore('name', () => { ... })`.
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

## Component Usage
- Call stores at the top of `<script setup>` or inside setup functions, getters, and actions.
- Use `storeToRefs()` when destructuring store state or getters in components.
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

## TypeScript
- Type store state, action payloads, and API responses explicitly.
- Avoid `any`; use `unknown` and narrow external inputs before committing them to state.
- Use interfaces for object state shared across components or API boundaries.
- Prefer explicit session fields (`sessionResolved`, `sessionError`) over a generic status enum unless a new workflow needs it.
- Keep store IDs stable and descriptive because they appear in devtools.

## Session And Side Effects
- Auth is cookie-based. Never store access tokens, refresh tokens, or authorization decisions in Pinia or browser storage.
- Bootstrap: `main.ts` mounts the app, then `restoreAuth()` (`client/src/plugins/auth.ts`) calls `resolveSession` after the router is ready.
- `resolveSession` / `sessionResolved` / `sessionError`: keep the prior user on non-401 failures (avoid bounce on network/5xx blips); clear the user only after confirmed auth failure.
- Deduplicate concurrent session restore with an in-flight promise (see `resolveInFlight` in the auth store).
- Use dynamic `import()` inside actions when needed to break circular dependencies (e.g. firebase sign-in, guest weather sync after login).
- Actions may be sync or async; keep each focused on one user or domain workflow.
- Validate action inputs at the boundary before mutating store state.
- Keep subscriptions, intervals, sockets, and browser listeners outside stores unless the store owns their lifecycle and cleanup.

## Router Guards And Browser State
- Use stores inside setup, getters, actions, or router guards where the active Pinia instance is available (`client/src/router/index.ts`).
- Do not read browser-only storage during module initialization in store files.
- Avoid singleton state that can outlive the current app instance in tests or previews.

## Persistence
- Do not add `pinia-plugin-persistedstate` or other Pinia persist plugins.
- Guest/local prefs and locations: use existing composables (`useLocalStorage`, weather location helpers), not Pinia.
- Authenticated preferences: API via store actions (`fetchPreferences` / `updatePreferences`) or composables that call the auth store.
- Treat any browser-stored values as untrusted input; validate before use in critical workflows.

## Testing And Tooling
- Primary pattern: `setActivePinia(createPinia())` in `beforeEach`; mock `@/composables/useApi`; test store actions directly (see `client/src/stores/auth.test.ts`).
- Reset Pinia between tests to avoid shared state leakage.
- `@pinia/testing` / `createTestingPinia` is optional for heavy component stubs only — do not install it unless a test clearly needs store stubs.
- `acceptHMRUpdate()` is optional for new stores; the project does not require it yet.
- Keep stores easy to inspect in Vue Devtools with clear state names and focused domains.

## Anti-Patterns
- Do not use Pinia as a dumping ground for every reactive value.
- Do not destructure state directly from a store without `storeToRefs()`.
- Do not mutate props or route objects through store actions.
- Do not put server-only objects, request instances (axios), DOM nodes, or timers in store state.
- Do not create circular reads between stores in setup functions; compose through actions or computed values instead.
- Do not grow a second god store; prefer a composable when state is feature-scoped.
- Do not read `localStorage` at module top-level in store files.
