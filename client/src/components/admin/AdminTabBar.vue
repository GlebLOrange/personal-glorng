<script setup lang="ts">
export interface AdminTab {
  id: string;
  label: string;
}

const activeTab = defineModel<string>({ required: true });

defineProps<{
  tabs: AdminTab[];
}>();

const tabClass = (id: string): string =>
  [
    "px-3 py-1.5 text-xs rounded-lg transition-colors",
    activeTab.value === id
      ? "bg-accent-blue/20 text-accent-blue"
      : "text-surface-mid hover:text-surface-light",
  ].join(" ");
</script>

<template>
  <div class="flex flex-wrap gap-2 mb-6">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      type="button"
      :class="tabClass(tab.id)"
      @click="activeTab = tab.id"
    >
      {{ tab.label }}
    </button>
  </div>
</template>
