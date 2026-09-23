<script setup lang="ts">
import { computed } from "vue";

import ExpenseCategoryChips from "@/components/expenses/ExpenseCategoryChips.vue";
import ExpenseList from "@/components/expenses/ExpenseList.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import SearchInput from "@/components/ui/SearchInput.vue";
import { Card } from "@/components/ui/card";
import type { CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExpenseSortKey } from "@/composables/useExpenseSort";
import type { ExchangeRates, Expense } from "@/types";

const productFilter = defineModel<string>("productFilter", { required: true });
const categoryFilter = defineModel<string | null>("categoryFilter", { required: true });
const displayCurrency = defineModel<CurrencyCode>("displayCurrency", { required: true });

defineProps<{
  categoryOptions: string[];
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

const hasTransactionFilters = computed(
  () => Boolean(productFilter.value.trim()) || categoryFilter.value !== null,
);
</script>

<template>
  <section
    id="expenses-tab-panel-transactions"
    role="tabpanel"
    aria-labelledby="expenses-tab-tab-transactions"
    tabindex="0"
    class="outline-none"
  >
    <Card variant="compact" class="flex w-full flex-col gap-2">
      <div class="flex items-center justify-between gap-2">
        <h3 class="text-sm font-semibold text-surface-light">recent transactions</h3>
        <p class="text-xs text-surface-mid">{{ expenseTotal }} items</p>
      </div>

      <div id="expense-transaction-filters" class="flex flex-col gap-2">
        <div class="flex min-w-0 flex-wrap items-center gap-2">
          <ExpenseCategoryChips
            v-model:category-filter="categoryFilter"
            :category-options="categoryOptions"
          />
          <SearchInput
            v-model="productFilter"
            class="min-w-0 flex-1"
            placeholder="filter by name"
            aria-label="filter by name"
            :min-length="1"
          />
        </div>
        <div v-if="hasTransactionFilters" class="flex flex-wrap items-center gap-2">
          <p class="text-xs text-surface-mid">
            <span v-if="productFilter.trim()">name: {{ productFilter.trim() }}</span>
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
    </Card>
  </section>
</template>
