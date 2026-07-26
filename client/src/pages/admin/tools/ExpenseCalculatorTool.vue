<script setup lang="ts">
import { computed } from "vue";

import ExpenseCalculatorShell from "@/components/expense-calculator/ExpenseCalculatorShell.vue";
import PageShell from "@/components/layout/PageShell.vue";
import { useExpenseCalculator } from "@/composables/useExpenseCalculator";
import { buildPersistenceHint } from "@/utils/expensePersistenceHint";

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
</script>

<template>
  <PageShell
    title="expense calculator"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'expense' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
    <ExpenseCalculatorShell
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
      @go-to-budget="switchMode('budget')"
    />
  </PageShell>
</template>
