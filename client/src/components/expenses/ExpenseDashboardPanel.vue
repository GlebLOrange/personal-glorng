<script setup lang="ts">
import { useTemplateRef } from "vue";

import ExpenseLedgerHeader from "@/components/expenses/ExpenseLedgerHeader.vue";
import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";
import { Card } from "@/components/ui/card";
import type { DateFilterMode, MonthPreset, CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExpenseSummary } from "@/types";

export type SmartExpensePayload = {
  tool_name: string;
  amount: string;
  currency: CurrencyCode;
  expense_date: string;
  category: string | null;
};

const monthPreset = defineModel<MonthPreset>("monthPreset", { required: true });
const dateFilterMode = defineModel<DateFilterMode>("dateFilterMode", { required: true });
const selectedMonth = defineModel<string>("selectedMonth", { required: true });
const dateFrom = defineModel<string>("dateFrom", { required: true });
const dateTo = defineModel<string>("dateTo", { required: true });
const displayCurrency = defineModel<CurrencyCode>("displayCurrency", { required: true });
const smartTextOpen = defineModel<boolean>("smartTextOpen", { required: true });
const quickAddCategory = defineModel<string>("quickAddCategory", { required: true });
const quickAddProduct = defineModel<string>("quickAddProduct", { required: true });
const quickAddPrice = defineModel<string>("quickAddPrice", { required: true });
const quickAddExpenseDate = defineModel<string>("quickAddExpenseDate", { required: true });
const quickAddNameError = defineModel<string | null>("quickAddNameError", { required: true });
const quickAddAmountError = defineModel<string | null>("quickAddAmountError", { required: true });

defineProps<{
  canWrite: boolean;
  savingExpense: boolean;
  categoryOptions: string[];
  productSuggestions: string[];
  monthLabel: string;
  hasActiveFilters: boolean;
  rangeError: string | null;
  summary: ExpenseSummary | null;
  summaryError: string | null;
  ratesError: string | null;
  formatMoney: (amount: string | number, currency: string) => string;
  expenseTotal: number;
}>();

const emit = defineEmits<{
  applyPreset: [preset: MonthPreset];
  clearFilters: [];
  retrySummary: [];
  submitQuick: [];
  smartSubmit: [payload: SmartExpensePayload];
  openTransactions: [];
}>();

const quickAddRef = useTemplateRef<InstanceType<typeof ExpenseQuickAdd>>("quickAddRef");

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
    id="expenses-tab-panel-expenses"
    role="tabpanel"
    aria-labelledby="expenses-tab-tab-expenses"
    tabindex="0"
    class="flex flex-col gap-6 outline-none"
  >
    <ExpenseLedgerHeader
      v-model:month-preset="monthPreset"
      v-model:date-filter-mode="dateFilterMode"
      v-model:selected-month="selectedMonth"
      v-model:date-from="dateFrom"
      v-model:date-to="dateTo"
      :month-label="monthLabel"
      :has-active-filters="hasActiveFilters"
      :range-error="rangeError"
      :summary="summary"
      :expense-total="expenseTotal"
      :format-money="formatMoney"
      :summary-error="summaryError"
      :rates-error="ratesError"
      @apply-preset="emit('applyPreset', $event)"
      @clear-filters="emit('clearFilters')"
      @retry="emit('retrySummary')"
      @open-transactions="emit('openTransactions')"
    />

    <Card variant="compact" class="flex flex-col gap-3">
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
  </section>
</template>
