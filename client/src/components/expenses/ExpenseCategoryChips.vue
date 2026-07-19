<script setup lang="ts">
defineProps<{
  categoryOptions: string[];
}>();

const categoryFilter = defineModel<string | null>("categoryFilter", { required: true });

const chipClass = (active: boolean) =>
  [
    "px-2.5 py-1 text-xs rounded-lg border transition-colors",
    active
      ? "bg-accent-blue/20 text-accent-blue border-accent-blue/40"
      : "text-surface-mid border-surface-border hover:text-surface-light",
  ].join(" ");
</script>

<template>
  <div class="flex flex-wrap gap-2" role="group" aria-label="Filter by category">
    <button
      type="button"
      :class="chipClass(categoryFilter === null)"
      :aria-pressed="categoryFilter === null"
      @click="categoryFilter = null"
    >
      all
    </button>
    <button
      v-for="category in categoryOptions"
      :key="category"
      type="button"
      :class="chipClass(categoryFilter === category)"
      :aria-pressed="categoryFilter === category"
      @click="categoryFilter = category"
    >
      {{ category }}
    </button>
  </div>
</template>
