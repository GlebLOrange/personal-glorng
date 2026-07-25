<script setup lang="ts">
import BackLink from "@/components/ui/BackLink.vue";
</script>

<template>
  <div class="flex flex-col items-center justify-center min-h-[60vh] gap-4">
    <h1 class="text-6xl font-bold text-status-error/80">404</h1>
    <p class="text-surface-mid">Page not found.</p>
    <BackLink to="/" />
  </div>
</template>
