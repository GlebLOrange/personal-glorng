<script setup lang="ts">
import { computed } from "vue";

import ExpenseCategoryOrbit from "@/components/expenses/ExpenseCategoryOrbit.vue";
import { Card } from "@/components/ui/card";
import type { ExpenseSummary } from "@/types";

const props = defineProps<{
  summary: ExpenseSummary | null;
  formatMoney: (amount: string | number, currency: string) => string;
}>();

const emit = defineEmits<{
  selectCategory: [category: string];
}>();

const currency = computed(() => props.summary?.currency ?? "PLN");

const rows = computed(() => {
  if (!props.summary?.by_category.length) return [];
  const total = parseFloat(String(props.summary.total));
  return [...props.summary.by_category]
    .map((item) => {
      const value = parseFloat(String(item.total));
      return {
        category: item.category,
        total: value,
        percent: total > 0 ? Math.round((value / total) * 100) : 0,
      };
    })
    .sort((a, b) => b.total - a.total);
});
</script>

<template>
  <div class="flex flex-col gap-4">
    <ExpenseCategoryOrbit
      framed
      :summary="summary"
      :format-money="formatMoney"
      @select-category="emit('selectCategory', $event)"
    />

    <Card>
      <h3 class="mb-3 text-sm font-semibold text-surface-light">category breakdown</h3>
      <ul v-if="rows.length" class="flex flex-col gap-3" aria-label="spend by category bars">
        <li v-for="row in rows" :key="row.category" class="flex flex-col gap-1">
          <div class="flex items-baseline justify-between gap-2 text-sm">
            <span class="min-w-0 truncate text-surface-light">{{ row.category }}</span>
            <span class="shrink-0 font-data text-surface-mid">
              {{ formatMoney(row.total, currency) }}
              <span class="ml-1 text-xs">{{ row.percent }}%</span>
            </span>
          </div>
          <div
            class="h-1.5 overflow-hidden rounded-full bg-surface-border"
            role="progressbar"
            :aria-valuenow="row.percent"
            aria-valuemin="0"
            aria-valuemax="100"
            :aria-label="`${row.category} ${row.percent}%`"
          >
            <div
              class="h-full rounded-full bg-accent-blue motion-reduce:transition-none transition-[width] duration-200"
              :style="{ width: `${Math.min(row.percent, 100)}%` }"
            />
          </div>
        </li>
      </ul>
      <p v-else class="text-sm text-surface-mid">No data available yet.</p>
    </Card>
  </div>
</template>
