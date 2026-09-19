<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref, useTemplateRef } from "vue";
import { useRoute } from "vue-router";

import ExpenseCategoryBreakdown from "@/components/expenses/ExpenseCategoryBreakdown.vue";
import ExpenseCategoryChips from "@/components/expenses/ExpenseCategoryChips.vue";
import ExpenseLedgerHeader from "@/components/expenses/ExpenseLedgerHeader.vue";
import ExpenseList from "@/components/expenses/ExpenseList.vue";
import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import SearchInput from "@/components/ui/SearchInput.vue";
import { Card } from "@/components/ui/card";
import type { DateFilterMode, MonthPreset, CurrencyCode } from "@/composables/useExpenseFilters";
import type { ExpenseSortKey } from "@/composables/useExpenseSort";
import type { ExchangeRates, Expense, ExpenseCategory, ExpenseSummary } from "@/types";

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
const productFilter = defineModel<string>("productFilter", { required: true });
const categoryFilter = defineModel<string | null>("categoryFilter", { required: true });
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
  listError: string | null;
  expenses: Expense[];
  listLoading: boolean;
  sortIndicator: (key: ExpenseSortKey) => string;
  sortAriaSort: (key: ExpenseSortKey) => "ascending" | "descending" | "none";
  monthLabel: string;
  hasActiveFilters: boolean;
  rangeError: string | null;
  summary: ExpenseSummary | null;
  expenseCategories: ExpenseCategory[];
  summaryError: string | null;
  ratesError: string | null;
  exchangeRates: ExchangeRates | null;
  formatMoney: (amount: string | number, currency: string) => string;
  formatExpenseDate: (iso: string) => string;
  convertAmount: (amount: string, from: CurrencyCode, to: CurrencyCode) => number;
  expenseTotal: number;
  expensePage: number;
  expensePages: number;
  hasNextExpensePage: boolean;
  hasPreviousExpensePage: boolean;
  hasChartData: boolean;
  lineChart: { labels: string[]; values: number[] };
  barChart: { labels: string[]; values: number[] };
  doughnutChart: { labels: string[]; values: number[] };
}>();

const emit = defineEmits<{
  applyPreset: [preset: MonthPreset];
  clearFilters: [];
  retrySummary: [];
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

const ExpenseInsights = defineAsyncComponent(
  () => import("@/components/expenses/ExpenseInsights.vue"),
);

const route = useRoute();
const quickAddRef = useTemplateRef<InstanceType<typeof ExpenseQuickAdd>>("quickAddRef");
const analyticsOpen = ref(route.hash === "#expenses-analytics");

const hasTransactionFilters = computed(
  () => Boolean(productFilter.value.trim()) || categoryFilter.value !== null,
);

function focusAddForm(): void {
  quickAddRef.value?.focusEntry();
}

onMounted(() => {
  if (route.hash !== "#expenses-analytics") return;
  analyticsOpen.value = true;
  document.getElementById("expenses-analytics")?.scrollIntoView({ behavior: "smooth" });
});

defineExpose({
  focusEntry: focusAddForm,
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
    />

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <Card class="flex flex-col gap-4">
        <h3 class="text-sm font-semibold text-surface-light">+ Add New Expense</h3>
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

      <div class="flex flex-col gap-6">
        <ExpenseCategoryBreakdown :summary="summary" :format-money="formatMoney" />

        <Card class="flex flex-col gap-3">
          <div class="flex items-center justify-between gap-2">
            <h3 class="text-sm font-semibold text-surface-light">Recent Transactions</h3>
            <p class="text-xs text-surface-mid">{{ expenseTotal }} items</p>
          </div>

          <div id="expense-transaction-filters" class="flex flex-col gap-2">
            <SearchInput
              v-model="productFilter"
              class="min-w-0 w-full"
              placeholder="filter by name"
              aria-label="filter by name"
              :min-length="1"
            />
            <ExpenseCategoryChips
              v-model:category-filter="categoryFilter"
              :category-options="categoryOptions"
            />
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
      </div>
    </div>

    <details
      id="expenses-analytics"
      class="group rounded-lg border border-surface-border/60"
      :open="analyticsOpen"
      @toggle="analyticsOpen = ($event.target as HTMLDetailsElement).open"
    >
      <summary
        class="cursor-pointer list-none px-4 py-3 text-sm font-medium text-surface-light marker:content-none [&::-webkit-details-marker]:hidden"
      >
        <span class="underline-offset-2 group-open:underline">Analytics</span>
        <span class="ml-2 text-xs font-normal text-surface-mid">charts and budgets</span>
      </summary>
      <div class="border-t border-surface-border/60 px-4 py-4">
        <ExpenseInsights
          :has-chart-data="hasChartData"
          :line-chart="lineChart"
          :bar-chart="barChart"
          :doughnut-chart="doughnutChart"
          :summary="summary"
          :expense-categories="expenseCategories"
          :format-money="formatMoney"
          @add-expense="focusAddForm"
        />
      </div>
    </details>
  </section>
</template>
