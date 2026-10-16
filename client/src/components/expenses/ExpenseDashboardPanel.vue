<script setup lang="ts">
import { computed, useTemplateRef } from "vue";

import ExpenseLedgerHeader from "@/components/expenses/ExpenseLedgerHeader.vue";
import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";
import { Card } from "@/components/ui/card";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { Expense, ExpenseSummary } from "@/types";

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
      :recent-expenses="recentExpenses"
      :format-money="formatMoney"
      :format-expense-date="formatExpenseDate"
      @retry="emit('retrySummary')"
      @open-activity="emit('openActivity')"
    />

    <Card variant="compact" class="flex flex-col gap-2">
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
