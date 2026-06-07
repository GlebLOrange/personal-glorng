<script setup lang="ts">
const year = new Date().getFullYear();
</script>

<template>
  <footer class="border-t border-surface-border py-10">
    <div class="flex justify-center mb-4">
      <router-link
        to="/privacy"
        class="text-base text-surface-sage hover:text-accent-blue transition-colors"
      >
        Privacy Policy
      </router-link>
    </div>
    <p class="text-base text-surface-sage text-center">
      &copy; {{ year }} <span class="text-accent-blue font-bold">Gleb Y.</span> Built with FastAPI +
      Vue 3.
    </p>
  </footer>
</template>
