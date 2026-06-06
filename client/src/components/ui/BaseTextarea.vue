<script setup lang="ts">
const model = defineModel<string>();

defineProps<{
  placeholder?: string;
  label?: string;
  rows?: number;
}>();
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" class="text-sm text-surface-mid">{{ label }}</label>
    <textarea
      v-model="model"
      :rows="rows ?? 5"
      :placeholder="placeholder"
      class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50 resize-y"
    />
  </div>
</template>
