<script setup lang="ts">
import { computed, useTemplateRef } from "vue";

import ExpenseLedgerHeader from "@/components/expenses/ExpenseLedgerHeader.vue";
import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { Expense, ExpenseCategory, ExpenseSummary } from "@/types";

export type SmartExpensePayload = {
  tool_name: string;
  amount: string;
  currency: CurrencyCode;
  expense_date: string;
  category: string | null;
};

const smartTextOpen = defineModel<boolean>("smartTextOpen", { required: true });
const quickAddCategory = defineModel<string>("quickAddCategory", { required: true });
const quickAddProduct = defineModel<string>("quickAddProduct", { required: true });
const quickAddPrice = defineModel<string>("quickAddPrice", { required: true });
const quickAddExpenseDate = defineModel<string>("quickAddExpenseDate", { required: true });
const quickAddNameError = defineModel<string | null>("quickAddNameError", { required: true });
const quickAddAmountError = defineModel<string | null>("quickAddAmountError", { required: true });
const displayCurrency = defineModel<CurrencyCode>("displayCurrency", { required: true });

const props = defineProps<{
  canWrite: boolean;
  savingExpense: boolean;
  categoryOptions: string[];
  productSuggestions: string[];
  monthLabel: string;
  summary: ExpenseSummary | null;
  summaryError: string | null;
  ratesError: string | null;
  expenseTotal: number;
  expenses: Expense[];
  expenseCategories: ExpenseCategory[];
  formatMoney: (amount: string | number, currency: string) => string;
  formatExpenseDate: (iso: string) => string;
}>();

const emit = defineEmits<{
  retrySummary: [];
  submitQuick: [];
  smartSubmit: [payload: SmartExpensePayload];
  openActivity: [];
}>();

const quickAddRef = useTemplateRef<InstanceType<typeof ExpenseQuickAdd>>("quickAddRef");

const currency = computed(() => props.summary?.currency ?? "PLN");

const topCategories = computed(() => {
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
    .sort((a, b) => b.total - a.total)
    .slice(0, 3);
});

const budgetAlerts = computed(() => {
  if (!props.summary) return [];
  const budgetByName = new Map<string, number>();
  for (const category of props.expenseCategories) {
    if (category.monthly_budget) {
      budgetByName.set(category.name, parseFloat(category.monthly_budget));
    }
  }
  return props.summary.by_category
    .map((item) => {
      const spent = parseFloat(String(item.total));
      const budget = budgetByName.get(item.category);
      if (budget == null || budget <= 0) return null;
      const percent = Math.round((spent / budget) * 100);
      return {
        category: item.category,
        spent,
        budget,
        percent,
        overBudget: percent > 100,
        warning: percent >= 80,
      };
    })
    .filter((row): row is NonNullable<typeof row> => row != null && row.warning);
});

const recentExpenses = computed(() => props.expenses.slice(0, 5));

defineExpose({
  focusEntry: () => {
    quickAddRef.value?.focusEntry();
  },
  focusSmartText: () => {
    quickAddRef.value?.focusSmartText();
  },
  clearSmartText: () => {
    quickAddRef.value?.clearSmartText();
  },
});
</script>

<template>
  <section
    id="expenses-tab-panel-today"
    role="tabpanel"
    aria-labelledby="expenses-tab-tab-today"
    tabindex="0"
    class="flex flex-col gap-4 outline-none"
  >
    <ExpenseLedgerHeader
      :month-label="monthLabel"
      :summary="summary"
      :expense-total="expenseTotal"
      :summary-error="summaryError"
      :rates-error="ratesError"
      @retry="emit('retrySummary')"
      @open-activity="emit('openActivity')"
    />

    <Card variant="compact" class="flex flex-col gap-2">
      <h3 class="text-sm font-semibold text-surface-light">add expense</h3>
      <ExpenseQuickAdd
        v-if="canWrite"
        ref="quickAddRef"
        v-model:category="quickAddCategory"
        v-model:product="quickAddProduct"
        v-model:price="quickAddPrice"
        v-model:expense-date="quickAddExpenseDate"
        v-model:name-error="quickAddNameError"
        v-model:amount-error="quickAddAmountError"
        v-model:currency="displayCurrency"
        v-model:smart-text-open="smartTextOpen"
        :loading="savingExpense"
        :category-options="categoryOptions"
        :product-suggestions="productSuggestions"
        @submit="emit('submitQuick')"
        @smart-submit="emit('smartSubmit', $event)"
      />
      <p v-else class="text-sm text-surface-mid">View only — you cannot add expenses.</p>
    </Card>

    <Card v-if="topCategories.length" variant="compact">
      <h3 class="mb-3 text-sm font-semibold text-surface-light">top categories</h3>
      <ul class="flex flex-col gap-2" aria-label="top categories this month">
        <li v-for="row in topCategories" :key="row.category" class="flex flex-col gap-1">
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
              class="h-full rounded-full bg-accent-blue"
              :style="{ width: `${Math.min(row.percent, 100)}%` }"
            />
          </div>
        </li>
      </ul>
    </Card>

    <Card v-if="budgetAlerts.length" variant="compact">
      <h3 class="mb-2 text-sm font-semibold text-surface-light">budget alerts</h3>
      <ul class="flex flex-col gap-2" aria-label="budget alerts">
        <li
          v-for="row in budgetAlerts"
          :key="row.category"
          class="text-sm"
          :class="row.overBudget ? 'text-status-error' : 'text-surface-light'"
        >
          {{ row.category }} — {{ row.percent }}%
          <span class="text-surface-mid">
            ({{ formatMoney(row.spent, currency) }} of {{ formatMoney(row.budget, currency) }})
          </span>
          <span v-if="row.overBudget" class="ml-1">over</span>
        </li>
      </ul>
    </Card>

    <Card variant="compact" class="flex flex-col gap-2">
      <div class="flex items-center justify-between gap-2">
        <h3 class="text-sm font-semibold text-surface-light">recent activity</h3>
        <BaseButton variant="ghost" quiet size="sm" @click="emit('openActivity')">
          view all
        </BaseButton>
      </div>
      <ul v-if="recentExpenses.length" class="flex flex-col gap-1.5" aria-label="recent expenses">
        <li
          v-for="expense in recentExpenses"
          :key="expense.id"
          class="flex items-baseline justify-between gap-2 text-sm"
        >
          <span class="min-w-0 truncate text-surface-light">
            {{ expense.tool_name }}
            <span class="text-xs text-surface-mid">
              · {{ formatExpenseDate(expense.expense_date) }}
            </span>
          </span>
          <span class="shrink-0 font-data text-surface-mid">
            {{ formatMoney(expense.amount, expense.currency) }}
          </span>
        </li>
      </ul>
      <p v-else class="text-sm text-surface-mid">No expenses this month yet.</p>
    </Card>
  </section>
</template>
