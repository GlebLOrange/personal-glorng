<script setup lang="ts">
defineEmits<{ close: [] }>();
</script>

<template>
  <div
    class="overlay-backdrop absolute inset-0 bg-surface-dark/80 backdrop-blur-sm"
    aria-hidden="true"
    @click="$emit('close')"
  />
</template>
