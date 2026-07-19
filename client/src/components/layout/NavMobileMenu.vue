<script setup lang="ts">
import { computed, nextTick, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import { useScrollLock } from "@/composables/useScrollLock";

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{ close: []; "go-home": [] }>();

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const menuRoot = ref<HTMLElement | null>(null);

const isPortfolio = computed(() => route.path === "/" || route.name === "home" || route.name === "portfolio");

const sectionLinks = [
  { href: "#about", label: "about" },
  { href: "#skills", label: "skills" },
  { href: "#experience", label: "experience" },
  { href: "#projects", label: "projects" },
  { href: "#contact", label: "contact" },
];

useScrollLock(() => props.open);

function focusableElements(): HTMLElement[] {
  const root = menuRoot.value;
  if (!root) return [];
  return Array.from(
    root.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
    ),
  );
}

function trapFocus(event: KeyboardEvent): void {
  const focusable = focusableElements();
  const first = focusable[0];
  const last = focusable.at(-1);
  if (!first || !last) return;

  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
    return;
  }
  if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape") {
    emit("close");
    return;
  }
  if (event.key === "Tab" && props.open) trapFocus(event);
}

function handleSectionClick(): void {
  emit("close");
}

function handleLogout(): void {
  auth.logout();
  emit("close");
  void router.push("/");
}

watch(
  () => route.fullPath,
  () => emit("close"),
);

watch(
  () => props.open,
  async (open) => {
    if (!open) {
      document.removeEventListener("keydown", onKeydown);
      return;
    }
    document.addEventListener("keydown", onKeydown);
    await nextTick();
    focusableElements()[0]?.focus();
  },
  { immediate: true },
);

onUnmounted(() => document.removeEventListener("keydown", onKeydown));
</script>

<template>
  <div
    v-if="open"
    id="nav-mobile-menu"
    ref="menuRoot"
    class="md:hidden border-t border-surface-border bg-surface-dark/95 backdrop-blur-md"
  >
    <div class="max-w-5xl mx-auto px-6 py-4 flex flex-col gap-1">
      <template v-if="isPortfolio">
        <p class="text-label text-surface-mid px-2 py-1 mb-1">On this page</p>
        <a
          v-for="link in sectionLinks"
          :key="link.href"
          :href="link.href"
          class="nav-link text-base px-3 py-3 rounded-lg hover:bg-surface-card"
          @click="handleSectionClick"
        >
          {{ link.label }}
        </a>

        <div class="border-t border-surface-border my-2" />
      </template>

      <RouterLink
        to="/"
        class="nav-link text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click.prevent="emit('go-home')"
      >
        portfolio
      </RouterLink>
      <RouterLink
        to="/news"
        class="nav-link text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click="emit('close')"
      >
        news
      </RouterLink>

      <RouterLink
        v-if="auth.isAuthenticated"
        to="/admin"
        class="nav-link-accent text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click="emit('close')"
      >
        admin
      </RouterLink>
      <RouterLink
        v-else
        to="/tools"
        class="nav-link-accent text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click="emit('close')"
      >
        tools
      </RouterLink>

      <RouterLink
        v-if="auth.isAuthenticated"
        to="/settings"
        class="nav-link text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click="emit('close')"
      >
        settings
      </RouterLink>

      <button
        v-if="auth.isAuthenticated"
        type="button"
        class="nav-link-violet text-base px-3 py-3 rounded-lg hover:bg-surface-card text-left"
        @click="handleLogout"
      >
        logout
      </button>
      <RouterLink
        v-else
        to="/login"
        class="nav-link-accent text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click="emit('close')"
      >
        login
      </RouterLink>
    </div>
  </div>
</template>
