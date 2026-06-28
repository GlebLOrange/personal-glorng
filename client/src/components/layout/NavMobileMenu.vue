<script setup lang="ts">
import { onMounted, onUnmounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{ close: [] }>();

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

const sectionLinks = [
  { href: "#skills", label: "Skills" },
  { href: "#experience", label: "Experience" },
  { href: "#projects", label: "Projects" },
  { href: "#contact", label: "Contact" },
];

function onKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape") {
    emit("close");
  }
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

onMounted(() => document.addEventListener("keydown", onKeydown));
onUnmounted(() => document.removeEventListener("keydown", onKeydown));
</script>

<template>
  <div
    v-if="open"
    id="nav-mobile-menu"
    class="md:hidden border-t border-surface-border bg-surface-dark/95 backdrop-blur-md"
  >
    <div class="max-w-5xl mx-auto px-6 py-4 flex flex-col gap-1">
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

      <RouterLink
        to="/"
        class="nav-link text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click="emit('close')"
      >
        Portfolio
      </RouterLink>
      <RouterLink
        to="/news"
        class="nav-link text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click="emit('close')"
      >
        News
      </RouterLink>

      <RouterLink
        v-if="auth.isAuthenticated"
        to="/admin"
        class="nav-link-accent text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click="emit('close')"
      >
        Tools
      </RouterLink>
      <RouterLink
        v-else
        to="/tools"
        class="nav-link-accent text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click="emit('close')"
      >
        Tools
      </RouterLink>

      <RouterLink
        v-if="auth.isAuthenticated"
        to="/settings"
        class="nav-link text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click="emit('close')"
      >
        Settings
      </RouterLink>

      <button
        v-if="auth.isAuthenticated"
        type="button"
        class="nav-link-violet text-base px-3 py-3 rounded-lg hover:bg-surface-card text-left"
        @click="handleLogout"
      >
        Logout
      </button>
      <RouterLink
        v-else
        to="/login"
        class="nav-link-accent text-base px-3 py-3 rounded-lg hover:bg-surface-card"
        @click="emit('close')"
      >
        Login
      </RouterLink>
    </div>
  </div>
</template>
