<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import type { ExpenseCalculatorBudgetRow } from "@/composables/useExpenseCalculator";
import type { CurrencyCode } from "@/composables/useExpenseFilters";

interface BudgetRowView {
  id: string;
  name: string;
  budget: number;
  spent: number;
  remaining: number;
  percent: number;
  overBudget: boolean;
}

const props = defineProps<{
  budgetRows: ExpenseCalculatorBudgetRow[];
  budgetSummary: {
    totalBudget: number;
    totalSpent: number;
    remaining: number;
    percent: number;
    overBudget: boolean;
    rows: BudgetRowView[];
  };
  displayCurrency: CurrencyCode;
  formatMoney: (amount: string | number, currency: string) => string;
}>();

const emit = defineEmits<{
  add: [];
  remove: [id: string];
}>();

const summaryById = computed(() => {
  const map = new Map<string, BudgetRowView>();
  for (const row of props.budgetSummary.rows) {
    map.set(row.id, row);
  }
  return map;
});
</script>

<template>
  <div class="flex flex-col gap-4">
    <Card variant="compact" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <p class="text-xs text-surface-mid uppercase tracking-wider">Budget</p>
        <p class="text-2xl font-bold font-data text-surface-light mt-1">
          {{ formatMoney(budgetSummary.totalBudget, displayCurrency) }}
        </p>
      </div>
      <div>
        <p class="text-xs text-surface-mid uppercase tracking-wider">Spent</p>
        <p class="text-2xl font-bold font-data text-surface-light mt-1">
          {{ formatMoney(budgetSummary.totalSpent, displayCurrency) }}
        </p>
      </div>
      <div>
        <p class="text-xs text-surface-mid uppercase tracking-wider">Remaining</p>
        <p
          class="text-2xl font-bold font-data mt-1"
          :class="budgetSummary.overBudget ? 'text-status-error' : 'text-accent-blue'"
        >
          {{ formatMoney(budgetSummary.remaining, displayCurrency) }}
        </p>
        <p class="text-xs text-surface-mid mt-1">
          <span v-if="budgetSummary.overBudget">Over budget</span>
          <span v-else>{{ budgetSummary.percent }}% used</span>
        </p>
      </div>
    </Card>

    <Card class="space-y-4">
      <div class="flex items-center justify-between gap-3">
        <p class="text-xs text-surface-mid uppercase tracking-wider">Categories</p>
        <BaseButton variant="primary" size="sm" @click="emit('add')">+ add category</BaseButton>
      </div>

      <ul role="list" class="space-y-4">
        <li
          v-for="row in budgetRows"
          :key="row.id"
          class="space-y-2 border-b border-surface-border pb-4 last:border-0 last:pb-0"
        >
          <div class="grid grid-cols-1 md:grid-cols-[1fr_120px_120px_auto] gap-3 items-end">
            <BaseInput
              v-model="row.name"
              placeholder="category (food, transport...)"
              aria-label="category (food, transport...)"
            />
            <BaseInput
              v-model="row.budget"
              type="number"
              step="0.01"
              min="0"
              placeholder="budget (0.00)"
              aria-label="budget (0.00)"
            />
            <BaseInput
              v-model="row.spent"
              type="number"
              step="0.01"
              min="0"
              placeholder="spent (0.00)"
              aria-label="spent (0.00)"
            />
            <BaseButton
              variant="ghost"
              size="sm"
              :aria-label="`Remove ${row.name || 'category'}`"
              class="md:mb-0.5"
              @click="emit('remove', row.id)"
            >
              remove
            </BaseButton>
          </div>

          <template
            v-for="view in [summaryById.get(row.id)]"
            :key="`${row.id}-summary`"
          >
            <div v-if="row.name.trim() && view" class="flex flex-col gap-1">
              <div class="flex justify-between text-xs">
                <span class="text-surface-mid">
                  {{ view.percent }}% ·
                  {{ formatMoney(view.remaining, displayCurrency) }}
                  {{ view.overBudget ? "over" : "left" }}
                </span>
                <span v-if="view.overBudget" class="text-status-error">Over budget</span>
              </div>
              <div class="h-1.5 bg-surface-border rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full motion-reduce:transition-none transition-all"
                  :class="view.overBudget ? 'bg-status-error' : 'bg-accent-blue'"
                  :style="{ width: `${Math.min(view.percent, 100)}%` }"
                />
              </div>
            </div>
          </template>
        </li>
      </ul>
    </Card>
  </div>
</template>
