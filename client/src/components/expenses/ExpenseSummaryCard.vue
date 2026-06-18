<script setup lang="ts">
import { computed } from "vue";

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

const budgetTotals = computed(() => {
  if (!props.summary) return null;
  const spent = categoryBreakdown.value.reduce(
    (total, item) => total + parseFloat(String(item.total)),
    0,
  );
  const budget = categoryBreakdown.value.reduce((total, item) => total + (item.budget ?? 0), 0);
  if (budget <= 0) return null;
  const percent = Math.round((spent / budget) * 100);
  return {
    spent,
    budget,
    percent,
    overBudget: percent > 100,
  };
});
</script>

<template>
  <section class="rounded-lg border border-surface-border bg-surface-card/70 p-4 md:p-5">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <p class="text-xs text-surface-mid uppercase tracking-wider">Total</p>
        <p v-if="summary" class="text-3xl font-bold text-surface-light font-data mt-1">
          {{ formatMoney(summary.total, summary.currency) }}
        </p>
        <p v-else class="text-3xl font-bold text-surface-border animate-pulse mt-1">—</p>
        <p class="text-xs text-surface-mid mt-1">{{ monthLabel }}</p>
      </div>

      <div class="rounded-lg border border-surface-border bg-surface-dark/40 p-3">
        <p class="text-xs text-surface-mid uppercase tracking-wider">Period change</p>
        <p
          v-if="periodChange"
          class="text-xl font-bold font-data mt-1"
          :class="periodChange.increased ? 'text-red-400' : 'text-green-400'"
        >
          {{ periodChange.increased ? "+" : "" }}{{ periodChange.delta }}%
        </p>
        <p v-else class="text-xl font-bold text-surface-border font-data mt-1">—</p>
        <p class="text-xs text-surface-mid mt-1">vs previous period</p>
      </div>

      <div class="rounded-lg border border-surface-border bg-surface-dark/40 p-3">
        <p class="text-xs text-surface-mid uppercase tracking-wider">Budget status</p>
        <p
          v-if="budgetTotals && summary"
          class="text-xl font-bold font-data mt-1"
          :class="budgetTotals.overBudget ? 'text-red-400' : 'text-accent-blue'"
        >
          {{ budgetTotals.percent }}%
        </p>
        <p v-else class="text-xl font-bold text-surface-border font-data mt-1">—</p>
        <p v-if="budgetTotals && summary" class="text-xs text-surface-mid mt-1">
          {{ formatMoney(budgetTotals.spent, summary.currency) }} of
          {{ formatMoney(budgetTotals.budget, summary.currency) }}
        </p>
        <p v-else class="text-xs text-surface-mid mt-1">No category budgets set</p>
      </div>
    </div>

    <div
      v-if="categoryBreakdown.length > 0"
      class="grid grid-cols-1 md:grid-cols-2 gap-3 border-t border-surface-border mt-5 pt-4"
    >
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
  </section>
</template>
