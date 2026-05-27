<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();

function handleLogout(): void {
  auth.logout();
}
</script>

<template>
  <nav class="sticky top-0 z-40 backdrop-blur-md bg-surface-dark/80 border-b border-surface-border">
    <div class="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
      <RouterLink to="/" class="text-xl font-bold accent-gradient">
        gLOrng
      </RouterLink>

      <div class="flex items-center gap-4 text-sm">
        <RouterLink to="/" class="text-surface-mid hover:text-surface-light transition-colors">
          Portfolio
        </RouterLink>

        <template v-if="auth.isAuthenticated">
          <RouterLink to="/admin" class="text-surface-mid hover:text-accent-blue transition-colors">
            Dashboard
          </RouterLink>
          <button
            class="text-surface-mid hover:text-accent-violet transition-colors"
            @click="handleLogout"
          >
            Logout
          </button>
        </template>

        <RouterLink
          v-else
          to="/login"
          class="text-surface-mid hover:text-accent-blue transition-colors"
        >
          Login
        </RouterLink>
      </div>
    </div>
  </nav>
</template>
