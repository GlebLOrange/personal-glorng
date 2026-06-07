<script setup lang="ts">
const model = defineModel<string | number | null>();

defineProps<{
  type?: string;
  placeholder?: string;
  label?: string;
}>();
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" class="text-sm text-surface-mid">{{ label }}</label>
    <input
      v-if="type === 'number'"
      v-model.number="model"
      type="number"
      :placeholder="placeholder"
      class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm font-data focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50"
    />
    <input
      v-else
      v-model="model"
      :type="type ?? 'text'"
      :placeholder="placeholder"
      class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50"
    />
  </div>
</template>
