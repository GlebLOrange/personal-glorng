<script setup lang="ts">
import { computed, useTemplateRef } from "vue";

import ExpenseCategoryChips from "@/components/expenses/ExpenseCategoryChips.vue";
import ExpenseList from "@/components/expenses/ExpenseList.vue";
import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExpenseSortKey } from "@/composables/useExpenseSort";
import type { ExchangeRates, Expense } from "@/types";

export type SmartExpensePayload = {
  tool_name: string;
  amount: string;
  currency: CurrencyCode;
  expense_date: string;
  category: string | null;
};

const productFilter = defineModel<string>("productFilter", { required: true });
const categoryFilter = defineModel<string | null>("categoryFilter", { required: true });
const displayCurrency = defineModel<CurrencyCode>("displayCurrency", { required: true });
const smartTextOpen = defineModel<boolean>("smartTextOpen", { required: true });
const filtersOpen = defineModel<boolean>("filtersOpen", { required: true });
const quickAddCategory = defineModel<string>("quickAddCategory", { required: true });
const quickAddProduct = defineModel<string>("quickAddProduct", { required: true });
const quickAddPrice = defineModel<string>("quickAddPrice", { required: true });

defineProps<{
  canWrite: boolean;
  savingExpense: boolean;
  categoryOptions: string[];
  productSuggestions: string[];
  listError: string | null;
  expenses: Expense[];
  listLoading: boolean;
  sortIndicator: (key: ExpenseSortKey) => string;
  sortAriaSort: (key: ExpenseSortKey) => "ascending" | "descending" | "none";
  monthLabel: string;
  exchangeRates: ExchangeRates | null;
  formatMoney: (amount: string | number, currency: string) => string;
  formatExpenseDate: (iso: string) => string;
  convertAmount: (amount: string, from: CurrencyCode, to: CurrencyCode) => number;
  expenseTotal: number;
  expensePage: number;
  expensePages: number;
  hasNextExpensePage: boolean;
  hasPreviousExpensePage: boolean;
}>();

const emit = defineEmits<{
  submitQuick: [];
  smartSubmit: [payload: SmartExpensePayload];
  clearTransactionFilters: [];
  retryList: [];
  edit: [expense: Expense];
  delete: [id: number];
  duplicate: [expense: Expense];
  sort: [key: ExpenseSortKey];
  smartText: [];
  firstPage: [];
  prevPage: [];
  nextPage: [];
  lastPage: [];
}>();

const quickAddRef = useTemplateRef<InstanceType<typeof ExpenseQuickAdd>>("quickAddRef");

const hasTransactionFilters = computed(
  () => Boolean(productFilter.value.trim()) || categoryFilter.value !== null,
);

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
    id="expenses-tab-panel-transactions"
    role="tabpanel"
    aria-labelledby="expenses-tab-tab-transactions"
    tabindex="0"
    class="flex flex-col gap-3 outline-none"
  >
    <ExpenseQuickAdd
      v-if="canWrite"
      ref="quickAddRef"
      v-model:category="quickAddCategory"
      v-model:product="quickAddProduct"
      v-model:price="quickAddPrice"
      v-model:currency="displayCurrency"
      v-model:smart-text-open="smartTextOpen"
      :loading="savingExpense"
      :category-options="categoryOptions"
      :product-suggestions="productSuggestions"
      @submit="emit('submitQuick')"
      @smart-submit="emit('smartSubmit', $event)"
    />

    <div
      v-if="filtersOpen || hasTransactionFilters"
      id="expense-transaction-filters"
      class="flex flex-col gap-2"
    >
      <ExpenseCategoryChips
        v-if="filtersOpen"
        v-model:category-filter="categoryFilter"
        :category-options="categoryOptions"
      />
      <div v-if="hasTransactionFilters" class="flex flex-wrap items-center gap-2">
        <p class="text-xs text-surface-mid">
          <span v-if="productFilter.trim()">product: {{ productFilter.trim() }}</span>
          <span v-if="productFilter.trim() && categoryFilter"> · </span>
          <span v-if="categoryFilter">category: {{ categoryFilter }}</span>
        </p>
        <BaseButton variant="ghost" size="sm" @click="emit('clearTransactionFilters')">
          clear filters
        </BaseButton>
      </div>
    </div>

    <ErrorState v-if="listError" :message="listError" show-retry @retry="emit('retryList')" />

    <ExpenseList
      :expenses="expenses"
      :loading="listLoading"
      :sort-indicator="sortIndicator"
      :sort-aria-sort="sortAriaSort"
      :month-label="monthLabel"
      :display-currency="displayCurrency"
      :exchange-rates="exchangeRates"
      :format-money="formatMoney"
      :format-expense-date="formatExpenseDate"
      :convert-amount="convertAmount"
      @edit="emit('edit', $event)"
      @delete="emit('delete', $event)"
      @duplicate="emit('duplicate', $event)"
      @sort="emit('sort', $event)"
      @smart-text="emit('smartText')"
    />

    <AdminListFooter
      v-if="expenses.length > 0"
      :total="expenseTotal"
      :page="expensePage"
      :total-pages="expensePages"
      :has-next-page="hasNextExpensePage"
      :has-previous-page="hasPreviousExpensePage"
      :loading="listLoading"
      item-label="expenses"
      aria-label="expenses pagination"
      @first="emit('firstPage')"
      @prev="emit('prevPage')"
      @next="emit('nextPage')"
      @last="emit('lastPage')"
    />
  </section>
</template>
