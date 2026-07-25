<script setup lang="ts">
import { useTemplateRef } from "vue";

import ExpenseCategoryChips from "@/components/expenses/ExpenseCategoryChips.vue";
import ExpenseList from "@/components/expenses/ExpenseList.vue";
import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import { Card } from "@/components/ui/card";
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

    <Card
      v-if="filtersOpen"
      id="expense-transaction-filters"
      variant="compact"
      class="flex flex-col gap-4"
    >
      <div class="flex flex-col gap-3 md:flex-row md:items-end">
        <div class="flex-1">
          <BaseInput
            v-model="productFilter"
            label="product filter"
            placeholder="filter by product..."
          />
        </div>
        <BaseButton
          v-if="productFilter || categoryFilter"
          variant="ghost"
          class="min-h-11"
          @click="emit('clearTransactionFilters')"
        >
          clear transaction filters
        </BaseButton>
      </div>

      <ExpenseCategoryChips
        v-model:category-filter="categoryFilter"
        :category-options="categoryOptions"
      />
    </Card>

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
      ariaLabel="Expenses pagination"
      @first="emit('firstPage')"
      @prev="emit('prevPage')"
      @next="emit('nextPage')"
      @last="emit('lastPage')"
    />
  </section>
</template>
