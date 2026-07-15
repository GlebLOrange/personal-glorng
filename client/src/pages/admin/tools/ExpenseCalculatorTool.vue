<script setup lang="ts">
import { computed } from "vue";

import ExpenseCalculatorBudget from "@/components/expense-calculator/ExpenseCalculatorBudget.vue";
import ExpenseCalculatorConvert from "@/components/expense-calculator/ExpenseCalculatorConvert.vue";
import ExpenseCalculatorLineItems from "@/components/expense-calculator/ExpenseCalculatorLineItems.vue";
import ExpenseCalculatorModeTabs from "@/components/expense-calculator/ExpenseCalculatorModeTabs.vue";
import ExpenseCalculatorWhatIf from "@/components/expense-calculator/ExpenseCalculatorWhatIf.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import { useExpenseCalculator } from "@/composables/useExpenseCalculator";

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

const persistenceHint = computed(() => {
  if (isSuperuser.value) {
    if (lastSavedAt.value && !stateDirty.value) {
      return `Saved ${new Date(lastSavedAt.value).toLocaleString()}`;
    }
    if (stateDirty.value) return "Unsaved changes";
    return "Superuser: save to keep data across sessions";
  }
  return "Calculations reset when you leave this page.";
});
</script>

<template>
  <PageShell
    title="expense calculator"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'expense calculator' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
    <div class="flex flex-col gap-4 min-w-0">
      <Card variant="compact" class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <p class="text-sm text-surface-mid">{{ persistenceHint }}</p>
        <div v-if="isSuperuser" class="flex flex-wrap gap-2">
          <BaseButton variant="ghost" size="sm" :disabled="loadingState" @click="loadState">
            {{ loadingState ? "Loading..." : "Load" }}
          </BaseButton>
          <BaseButton variant="primary" size="sm" :disabled="saving || !stateDirty" @click="saveState">
            {{ saving ? "Saving..." : "Save" }}
          </BaseButton>
        </div>
      </Card>

      <div class="flex flex-col md:flex-row md:items-end gap-3">
        <ExpenseCalculatorModeTabs
          class="flex-1"
          :active-mode="activeMode"
          :tabs="modeTabs"
          @change="switchMode"
        />
        <div class="md:w-36">
          <label class="text-sm text-surface-mid block mb-1">Display currency</label>
          <select
            v-model="displayCurrency"
            class="w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue h-[42px]"
          >
            <option value="PLN">PLN</option>
            <option value="EUR">EUR</option>
            <option value="USD">USD</option>
            <option value="BYN">BYN</option>
          </select>
        </div>
      </div>

      <section
        v-if="activeMode === 'convert'"
        id="expense-calc-panel-convert"
        role="tabpanel"
        aria-labelledby="expense-calc-tab-convert"
        tabindex="0"
        class="outline-none"
      >
        <ExpenseCalculatorConvert :exchange-rates="exchangeRates" :rates-loading="ratesLoading" />
      </section>

      <section
        v-else-if="activeMode === 'sum'"
        id="expense-calc-panel-sum"
        role="tabpanel"
        aria-labelledby="expense-calc-tab-sum"
        tabindex="0"
        class="outline-none"
      >
        <ExpenseCalculatorLineItems
          :line-items="lineItems"
          :display-currency="displayCurrency"
          :sum-total="sumTotal"
          :format-money="formatMoney"
          @add="addLineItem"
          @remove="removeLineItem"
          @apply-to-budget="applySumToBudget"
        />
      </section>

      <section
        v-else-if="activeMode === 'budget'"
        id="expense-calc-panel-budget"
        role="tabpanel"
        aria-labelledby="expense-calc-tab-budget"
        tabindex="0"
        class="outline-none"
      >
        <ExpenseCalculatorBudget
          :budget-rows="budgetRows"
          :budget-summary="budgetSummary"
          :display-currency="displayCurrency"
          :format-money="formatMoney"
          @add="addBudgetRow"
          @remove="removeBudgetRow"
        />
      </section>

      <section
        v-else-if="activeMode === 'whatif'"
        id="expense-calc-panel-whatif"
        role="tabpanel"
        aria-labelledby="expense-calc-tab-whatif"
        tabindex="0"
        class="outline-none"
      >
        <ExpenseCalculatorWhatIf
          v-model:what-if-category-id="whatIfCategoryId"
          v-model:what-if-amount="whatIfAmount"
          v-model:what-if-currency="whatIfCurrency"
          :budget-options="budgetOptions"
          :display-currency="displayCurrency"
          :projection="whatIfProjection"
          :format-money="formatMoney"
        />
      </section>
    </div>
  </PageShell>
</template>
