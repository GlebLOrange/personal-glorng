<script setup lang="ts">
import BackLink from "@/components/ui/BackLink.vue";
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-[60vh] gap-4 px-4">
    <h1 class="text-6xl font-bold text-status-error/80">404</h1>
    <p class="text-surface-mid">Page not found.</p>
    <nav aria-label="Recovery links" class="flex flex-wrap items-center justify-center gap-4">
      <RouterLink to="/" class="nav-link text-sm">Home</RouterLink>
      <RouterLink to="/tools" class="nav-link text-sm">Tools</RouterLink>
      <RouterLink to="/news" class="nav-link text-sm">News</RouterLink>
    </nav>
    <BackLink to="/" />
  </div>
</template>
