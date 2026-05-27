<script setup lang="ts">
defineProps<{
  title?: string;
}>();
</script>

<template>
  <div class="code-block">
    <div v-if="title" class="text-xs text-surface-mid mb-2 uppercase tracking-wider">{{ title }}</div>
    <pre class="text-sm leading-relaxed"><slot /></pre>
  </div>
</template>
