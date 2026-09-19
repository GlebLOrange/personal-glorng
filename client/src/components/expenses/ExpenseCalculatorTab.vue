<script setup lang="ts">
import { computed } from "vue";

import ExpenseCalculatorPanel from "@/components/expenses/ExpenseCalculatorPanel.vue";
import { useExpenseCalculator } from "@/composables/useExpenseCalculator";
import { buildPersistenceHint } from "@/utils/expensePersistenceHint";

/** Owns calculator state so ExpensesTool does not boot rates/state on other tabs. */
const {
  activeMode,
  modeTabs,
  switchMode,
  exchangeRates,
  ratesLoading,
  displayCurrency,
  lineItems,
  budgetRows,
  whatIfCategoryId,
  whatIfAmount,
  whatIfCurrency,
  sumTotal,
  budgetSummary,
  whatIfProjection,
  isSuperuser,
  stateDirty,
  lastSavedAt,
  saving,
  loadingState,
  formatMoney,
  addLineItem,
  removeLineItem,
  addBudgetRow,
  removeBudgetRow,
  applySumToBudget,
  saveState,
  loadState,
} = useExpenseCalculator();

const budgetOptions = computed(() =>
  budgetRows.value
    .filter((row) => row.name.trim())
    .map((row) => ({ id: row.id, name: row.name.trim() })),
);

const persistenceHint = computed(() =>
  buildPersistenceHint({
    isSuperuser: isSuperuser.value,
    stateDirty: stateDirty.value,
    lastSavedAt: lastSavedAt.value,
  }),
);

function goToBudgetMode(): void {
  switchMode("budget");
}
</script>

<template>
  <ExpenseCalculatorPanel
    v-model:display-currency="displayCurrency"
    v-model:what-if-category-id="whatIfCategoryId"
    v-model:what-if-amount="whatIfAmount"
    v-model:what-if-currency="whatIfCurrency"
    :persistence-hint="persistenceHint"
    :is-superuser="isSuperuser"
    :loading-state="loadingState"
    :saving="saving"
    :state-dirty="stateDirty"
    :active-mode="activeMode"
    :mode-tabs="modeTabs"
    :exchange-rates="exchangeRates"
    :rates-loading="ratesLoading"
    :line-items="lineItems"
    :sum-total="sumTotal"
    :budget-rows="budgetRows"
    :budget-summary="budgetSummary"
    :budget-options="budgetOptions"
    :what-if-projection="whatIfProjection"
    :format-money="formatMoney"
    @load-state="loadState"
    @save-state="saveState"
    @change-mode="switchMode"
    @add-line-item="addLineItem"
    @remove-line-item="removeLineItem"
    @apply-sum-to-budget="applySumToBudget"
    @add-budget-row="addBudgetRow"
    @remove-budget-row="removeBudgetRow"
    @go-to-budget="goToBudgetMode"
  />
</template>
