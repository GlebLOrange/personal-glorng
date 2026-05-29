<script setup lang="ts">
const year = new Date().getFullYear();
</script>

<template>
  <footer class="border-t border-surface-border py-8 font-mono">
    <div class="flex justify-center mb-4">
      <router-link
        to="/privacy"
        class="text-sm text-surface-mid hover:text-accent-blue transition-colors"
      >
        Privacy Policy
      </router-link>
    </div>
    <p class="text-sm text-surface-mid text-center">
      &copy; {{ year }} <span class="accent-gradient font-bold">gLOrng</span>. Built with FastAPI +
      Vue 3.
    </p>
  </footer>
</template>
