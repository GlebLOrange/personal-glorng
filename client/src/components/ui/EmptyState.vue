<script setup lang="ts">
defineProps<{
  title?: string;
  description?: string;
}>();
</script>

<template>
  <div role="status" class="py-8 text-center">
    <h3 v-if="title" class="card-title mb-2">{{ title }}</h3>
    <p v-if="description" class="text-sm text-surface-mid" :class="{ 'mb-4': $slots.action }">
      {{ description }}
    </p>
    <p v-else-if="$slots.default" class="text-sm text-surface-mid" :class="{ 'mb-4': $slots.action }">
      <slot />
    </p>
    <div v-if="$slots.action">
      <slot name="action" />
    </div>
  </div>
</template>
