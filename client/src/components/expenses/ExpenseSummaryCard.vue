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

defineExpose({ categoryBreakdown, budgetTotals });
</script>

<template>
  <div class="flex flex-col gap-4">
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
          :aria-label="`Budget used ${budgetTotals.percent}%`"
        >
          <div
            class="h-full rounded-full transition-[width] duration-200"
            :class="budgetTotals.overBudget ? 'bg-status-error' : 'bg-accent-blue'"
            :style="{ width: `${Math.min(budgetTotals.percent, 100)}%` }"
          />
        </div>
      </div>
    </div>

    <div
      v-if="categoryBreakdown.length > 0"
      class="grid grid-cols-1 gap-3 border-t border-surface-border pt-4 md:grid-cols-2"
    >
      <div v-for="item in categoryBreakdown" :key="item.category" class="flex flex-col gap-1">
        <div class="flex justify-between gap-2 text-xs">
          <span class="text-surface-light">{{ item.category }}</span>
          <span class="shrink-0 font-data text-surface-mid">
            {{ formatMoney(item.total, summary!.currency) }}
            <span v-if="item.budget" class="text-surface-mid/70">
              · {{ item.budgetPercent }}% of
              {{ formatMoney(item.budget, summary!.currency) }}
            </span>
            <span v-else class="text-surface-mid/70">· {{ item.percent }}%</span>
          </span>
        </div>
        <div class="h-1.5 overflow-hidden rounded-full bg-surface-border">
          <div
            class="h-full rounded-full transition-[width] duration-200"
            :class="item.overBudget ? 'bg-status-error' : 'bg-accent-blue'"
            :style="{
              width: `${Math.min(item.budgetPercent ?? item.percent, 100)}%`,
            }"
          />
        </div>
      </div>
    </div>
  </div>
</template>
