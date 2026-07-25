<script setup lang="ts">
import ExpenseCalculatorShell from "@/components/expense-calculator/ExpenseCalculatorShell.vue";
import type {
  ExpenseCalculatorBudgetRow,
  ExpenseCalculatorLineItem,
  ExpenseCalculatorMode,
} from "@/composables/useExpenseCalculator";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExchangeRates } from "@/types";

const displayCurrency = defineModel<CurrencyCode>("displayCurrency", { required: true });
const whatIfCategoryId = defineModel<string>("whatIfCategoryId", { required: true });
const whatIfAmount = defineModel<string>("whatIfAmount", { required: true });
const whatIfCurrency = defineModel<CurrencyCode>("whatIfCurrency", { required: true });

defineProps<{
  persistenceHint: string;
  isSuperuser: boolean;
  loadingState: boolean;
  saving: boolean;
  stateDirty: boolean;
  activeMode: ExpenseCalculatorMode;
  modeTabs: { id: ExpenseCalculatorMode; label: string }[];
  exchangeRates: ExchangeRates | null;
  ratesLoading: boolean;
  lineItems: ExpenseCalculatorLineItem[];
  sumTotal: number;
  budgetRows: ExpenseCalculatorBudgetRow[];
  budgetSummary: {
    totalBudget: number;
    totalSpent: number;
    remaining: number;
    percent: number;
    overBudget: boolean;
    rows: Array<{
      id: string;
      name: string;
      budget: number;
      spent: number;
      remaining: number;
      percent: number;
      overBudget: boolean;
    }>;
  };
  budgetOptions: { id: string; name: string }[];
  whatIfProjection: {
    amount: number;
    budget: number;
    spent: number;
    projected: number;
    remaining: number;
    overBudget: boolean;
    overBy: number;
    withinBudget: boolean;
  };
  formatMoney: (amount: string | number, currency: string) => string;
}>();

const emit = defineEmits<{
  loadState: [];
  saveState: [];
  changeMode: [mode: ExpenseCalculatorMode];
  addLineItem: [];
  removeLineItem: [id: string];
  applySumToBudget: [];
  addBudgetRow: [];
  removeBudgetRow: [id: string];
  goToBudget: [];
}>();
</script>

<template>
  <ExpenseCalculatorShell
    v-model:display-currency="displayCurrency"
    v-model:what-if-category-id="whatIfCategoryId"
    v-model:what-if-amount="whatIfAmount"
    v-model:what-if-currency="whatIfCurrency"
    tabpanel-id="expenses-tab-panel-calculator"
    tabpanel-labelled-by="expenses-tab-tab-calculator"
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
    @load-state="emit('loadState')"
    @save-state="emit('saveState')"
    @change-mode="emit('changeMode', $event)"
    @add-line-item="emit('addLineItem')"
    @remove-line-item="emit('removeLineItem', $event)"
    @apply-sum-to-budget="emit('applySumToBudget')"
    @add-budget-row="emit('addBudgetRow')"
    @remove-budget-row="emit('removeBudgetRow', $event)"
    @go-to-budget="emit('goToBudget')"
  />
</template>
