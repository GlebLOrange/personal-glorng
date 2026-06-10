<script setup lang="ts">
import { computed } from "vue";

import BaseCard from "@/components/ui/BaseCard.vue";
import type { ExpenseCategory, ExpenseSummary } from "@/types";

const props = defineProps<{
  summary: ExpenseSummary | null;
  monthLabel: string;
  expenseCategories: ExpenseCategory[];
  periodChange: { delta: number; increased: boolean } | null;
  formatMoney: (amount: string | number, currency: string) => string;
}>();

const budgetByCategory = computed(() => {
  const map = new Map<string, number>();
  for (const category of props.expenseCategories) {
    if (category.monthly_budget) {
      map.set(category.name, parseFloat(category.monthly_budget));
    }
  }
  return map;
});

const categoryBreakdown = computed(() => {
  if (!props.summary || props.summary.by_category.length === 0) return [];
  const total = parseFloat(String(props.summary.total));
  if (total <= 0) return [];

  return props.summary.by_category.map((item) => {
    const value = parseFloat(String(item.total));
    const budget = budgetByCategory.value.get(item.category) ?? null;
    const budgetPercent = budget && budget > 0 ? Math.round((value / budget) * 100) : null;
    return {
      category: item.category,
      total: item.total,
      percent: Math.round((value / total) * 100),
      budget,
      budgetPercent,
      overBudget: budgetPercent !== null && budgetPercent > 100,
    };
  });
});
</script>

<template>
  <BaseCard class="flex flex-col gap-4">
    <div>
      <p class="text-xs text-surface-mid uppercase tracking-wider">Total for {{ monthLabel }}</p>
      <p v-if="summary" class="text-2xl font-bold text-surface-light font-data">
        {{ formatMoney(summary.total, summary.currency) }}
      </p>
      <p v-else class="text-2xl font-bold text-surface-border animate-pulse">—</p>
      <p
        v-if="periodChange"
        class="text-xs mt-1 font-data"
        :class="periodChange.increased ? 'text-red-400' : 'text-green-400'"
      >
        {{ periodChange.increased ? "+" : "" }}{{ periodChange.delta }}% vs previous period
      </p>
    </div>

    <div
      v-if="categoryBreakdown.length > 0"
      class="flex flex-col gap-2 border-t border-surface-border pt-3"
    >
      <p class="text-xs text-surface-mid uppercase tracking-wider">By category</p>
      <div v-for="item in categoryBreakdown" :key="item.category" class="flex flex-col gap-1">
        <div class="flex justify-between text-xs">
          <span class="text-surface-light">{{ item.category }}</span>
          <span class="text-surface-mid font-data">
            {{ formatMoney(item.total, summary!.currency) }}
            <span v-if="item.budget" class="text-surface-mid/70">
              · {{ item.budgetPercent }}% of
              {{ formatMoney(item.budget, summary!.currency) }}
            </span>
            <span v-else class="text-surface-mid/70">· {{ item.percent }}%</span>
          </span>
        </div>
        <div class="h-1.5 bg-surface-border rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all"
            :class="item.overBudget ? 'bg-red-400' : 'bg-accent-blue'"
            :style="{
              width: `${Math.min(item.budgetPercent ?? item.percent, 100)}%`,
            }"
          />
        </div>
      </div>
    </div>
  </BaseCard>
</template>
