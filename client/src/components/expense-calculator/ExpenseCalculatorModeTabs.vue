<script setup lang="ts">
import type { ExpenseCalculatorMode } from "@/composables/useExpenseCalculator";

defineProps<{
  activeMode: ExpenseCalculatorMode;
  tabs: Array<{ id: ExpenseCalculatorMode; label: string }>;
}>();

const emit = defineEmits<{ change: [mode: ExpenseCalculatorMode] }>();
</script>

<template>
  <div
    role="tablist"
    aria-label="Calculator modes"
    class="flex flex-wrap gap-1 rounded-lg border border-surface-border bg-surface-dark/40 p-1"
  >
    <button
      v-for="tab in tabs"
      :key="tab.id"
      :id="`expense-calc-tab-${tab.id}`"
      type="button"
      role="tab"
      :aria-selected="activeMode === tab.id"
      :aria-controls="`expense-calc-panel-${tab.id}`"
      class="flex-1 min-w-[5rem] rounded-md px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue"
      :class="
        activeMode === tab.id
          ? 'bg-surface-card text-surface-light'
          : 'text-surface-mid hover:text-surface-light'
      "
      @click="emit('change', tab.id)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>
