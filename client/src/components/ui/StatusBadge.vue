<script setup lang="ts">
defineProps<{
  label: string;
  className: string;
}>();
</script>

<template>
  <span :class="['text-xs px-2 py-0.5 rounded border', className]">{{ label }}</span>
</template>
