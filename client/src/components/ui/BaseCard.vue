<script setup lang="ts">
defineProps<{
  hoverable?: boolean;
}>();
</script>

<template>
  <div
    :class="[
      'bg-surface-card border border-surface-border rounded-lg p-6',
      hoverable && 'hover:border-accent-blue transition-colors duration-200',
    ]"
  >
    <slot />
  </div>
</template>
