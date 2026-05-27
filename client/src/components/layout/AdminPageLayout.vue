<script setup lang="ts">
defineProps<{
  title: string;
  maxWidth?: "sm" | "md" | "lg" | "xl";
}>();
</script>

<template>
  <div
    :class="[
      'mx-auto px-6 py-16',
      maxWidth === 'sm' ? 'max-w-sm'
        : maxWidth === 'md' ? 'max-w-3xl'
        : maxWidth === 'xl' ? 'max-w-5xl'
        : 'max-w-3xl',
    ]"
  >
    <h1 class="text-2xl font-bold text-surface-light mb-8">
      <span class="accent-gradient">€ {{ title }}</span>
    </h1>
    <slot />
  </div>
</template>
