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

/** KPI-only totals; category bars live on Insights. */
const budgetTotals = computed(() => {
  if (!props.summary || props.summary.by_category.length === 0) return null;
  const total = parseFloat(String(props.summary.total));
  if (total <= 0) return null;

  let spent = 0;
  let budget = 0;
  for (const item of props.summary.by_category) {
    spent += parseFloat(String(item.total));
    budget += budgetByCategory.value.get(item.category) ?? 0;
  }
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
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
    <div>
      <p class="text-xs text-surface-mid">total</p>
      <p v-if="summary" class="mt-1 text-3xl font-bold font-data text-surface-light">
        {{ formatMoney(summary.total, summary.currency) }}
      </p>
      <p v-else class="mt-1 animate-pulse text-3xl font-bold text-surface-border">—</p>
      <p class="mt-1 text-xs text-surface-mid">{{ monthLabel }}</p>
    </div>

    <div>
      <p class="text-xs text-surface-mid">period change</p>
      <p
        v-if="periodChange"
        class="mt-1 text-xl font-bold font-data"
        :class="periodChange.increased ? 'text-status-error' : 'text-status-success'"
      >
        {{ periodChange.increased ? "+" : "" }}{{ periodChange.delta }}%
        <span class="sr-only">
          {{ periodChange.increased ? "increase" : "decrease" }} versus previous period
        </span>
      </p>
      <p v-else class="mt-1 text-xl font-bold font-data text-surface-border">—</p>
      <p class="mt-1 text-xs text-surface-mid">vs previous period</p>
    </div>

    <div>
      <p class="text-xs text-surface-mid">budget status</p>
      <p
        v-if="budgetTotals && summary"
        class="mt-1 text-xl font-bold font-data"
        :class="budgetTotals.overBudget ? 'text-status-error' : 'text-accent-blue'"
      >
        {{ budgetTotals.percent }}%
        <span class="sr-only">
          of budget{{ budgetTotals.overBudget ? ", over budget" : "" }}
        </span>
      </p>
      <p v-else class="mt-1 text-xl font-bold font-data text-surface-border">—</p>
      <p v-if="budgetTotals && summary" class="mt-1 text-xs text-surface-mid">
        {{ formatMoney(budgetTotals.spent, summary.currency) }} of
        {{ formatMoney(budgetTotals.budget, summary.currency) }}
      </p>
      <p v-else class="mt-1 text-xs text-surface-mid">No category budgets set</p>
      <div
        v-if="budgetTotals"
        class="mt-2 h-1.5 overflow-hidden rounded-full bg-surface-border"
        role="progressbar"
        :aria-valuenow="Math.min(budgetTotals.percent, 100)"
        aria-valuemin="0"
        aria-valuemax="100"
        :aria-label="`budget used ${budgetTotals.percent}%`"
      >
        <div
          class="h-full rounded-full transition-[width] duration-200"
          :class="budgetTotals.overBudget ? 'bg-status-error' : 'bg-accent-blue'"
          :style="{ width: `${Math.min(budgetTotals.percent, 100)}%` }"
        />
      </div>
    </div>
  </div>
</template>
