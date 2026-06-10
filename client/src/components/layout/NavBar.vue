<script setup lang="ts">
import { ref } from "vue";

import NavMobileMenu from "@/components/layout/NavMobileMenu.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const mobileOpen = ref(false);

function handleLogout(): void {
  auth.logout();
}

function toggleMobileMenu(): void {
  mobileOpen.value = !mobileOpen.value;
}

function closeMobileMenu(): void {
  mobileOpen.value = false;
}
</script>

<template>
  <div>
    <nav
      aria-label="Main navigation"
      class="sticky top-0 z-40 backdrop-blur-md bg-surface-dark/80 border-b border-surface-border"
    >
      <div class="max-w-5xl mx-auto px-6 py-4 md:py-5 flex items-center justify-between">
        <RouterLink to="/" class="text-xl font-bold text-surface-light" @click="closeMobileMenu">
          Gleb.Y
        </RouterLink>

        <div class="hidden md:flex items-center gap-5 text-base">
          <RouterLink to="/" class="nav-link px-2 py-1"> portfolio </RouterLink>

          <RouterLink v-if="auth.isAuthenticated" to="/admin" class="nav-link-accent px-2 py-1">
            tools
          </RouterLink>
          <RouterLink v-else to="/tools" class="nav-link-accent px-2 py-1"> tools </RouterLink>

          <RouterLink v-if="auth.isAuthenticated" to="/settings" class="nav-link px-2 py-1">
            settings
          </RouterLink>

          <button
            v-if="auth.isAuthenticated"
            type="button"
            class="nav-link-violet px-2 py-1"
            @click="handleLogout"
          >
            logout
          </button>
          <RouterLink v-else to="/login" class="nav-link-accent px-2 py-1"> login </RouterLink>
        </div>

        <button
          type="button"
          class="md:hidden interactive-surface px-3 py-2 text-surface-light"
          :aria-expanded="mobileOpen"
          aria-controls="nav-mobile-menu"
          aria-label="Toggle navigation menu"
          @click="toggleMobileMenu"
        >
          <span class="sr-only">Menu</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="size-5"
            aria-hidden="true"
          >
            <path v-if="!mobileOpen" stroke-linecap="round" d="M4 7h16M4 12h16M4 17h16" />
            <path v-else stroke-linecap="round" d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      </div>
    </nav>

    <NavMobileMenu :open="mobileOpen" @close="closeMobileMenu" />
  </div>
</template>
