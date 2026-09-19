<script setup lang="ts">
import { computed, defineAsyncComponent, useTemplateRef } from "vue";

import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import ExpenseFormDrawer from "@/components/expenses/ExpenseFormDrawer.vue";
import ExpenseLedgerHeader from "@/components/expenses/ExpenseLedgerHeader.vue";
import ExpenseTransactionsPanel from "@/components/expenses/ExpenseTransactionsPanel.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import FilterIcon from "@/components/icons/FilterIcon.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import SearchInput from "@/components/ui/SearchInput.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import {
  isCalculatorTab,
  useExpensesTool,
  type ExpenseQuickAddTarget,
} from "@/composables/useExpensesTool";
import { usePermissions } from "@/composables/usePermissions";

const ExpenseInsights = defineAsyncComponent(
  () => import("@/components/expenses/ExpenseInsights.vue"),
);
const ExpenseCalculatorTab = defineAsyncComponent(
  () => import("@/components/expenses/ExpenseCalculatorTab.vue"),
);
const ExpenseCategorySettings = defineAsyncComponent(
  () => import("@/components/expenses/ExpenseCategorySettings.vue"),
);

const transactionsPanelRef = useTemplateRef<ExpenseQuickAddTarget>("transactionsPanelRef");

const {
  activeTab,
  expenseTabItems,
  savingExpense,
  exporting,
  deletingExpense,
  deletingCategory,
  smartTextOpen,
  filtersOpen,
  showForm,
  deleteTargetId,
  deleteCategoryTarget,
  expensePage,
  displayCurrency,
  expenses,
  expensePages,
  summary,
  periodChange,
  exchangeRates,
  listLoading,
  lineChart,
  barChart,
  doughnutChart,
  hasChartData,
  convertAmount,
  formatMoney,
  formatExpenseDate,
  listError,
  summaryError,
  ratesError,
  loadSummary,
  loadRates,
  expenseCategories,
  newCategoryName,
  editingCategoryId,
  editingCategoryName,
  editingCategoryBudget,
  categoryOptions,
  addCategory,
  startEditCategory,
  cancelEditCategory,
  saveCategoryRename,
  monthPreset,
  dateFilterMode,
  selectedMonth,
  dateFrom,
  dateTo,
  productFilter,
  categoryFilter,
  monthLabel,
  hasActiveFilters,
  rangeError,
  clearFilters,
  quickAdd,
  form,
  formTitle,
  expenseTotal,
  hasPreviousExpensePage,
  hasNextExpensePage,
  transactionFilterLabel,
  productSuggestions,
  sortIndicator,
  sortAriaSort,
  handleDatePreset,
  clearTransactionFilters,
  goToExpensePage,
  handleExpenseSort,
  openEdit,
  openCreate,
  openSmartText,
  duplicateExpense,
  exportCsv,
  requestDeleteExpense,
  confirmDeleteExpense,
  requestDeleteCategory,
  confirmDeleteCategory,
  switchTab,
  saveExpense,
  quickSaveExpense,
  saveSmartExpense,
} = useExpensesTool(transactionsPanelRef);

const showLedgerHeader = computed(() => !isCalculatorTab(activeTab.value));

const { can } = usePermissions();
const canWriteExpenses = computed(() => can("expenses", "write"));

function retrySummaryAndRates(): void {
  void Promise.all([loadSummary(), loadRates()]);
}

function goToTransactions(): void {
  switchTab("transactions");
}
</script>

<template>
  <AdminPageLayout hub="tools" title="expenses" max-width="xl">
    <div class="min-w-0">
      <div class="flex flex-col gap-3">
        <p
          v-if="!canWriteExpenses"
          class="rounded-lg bg-surface-dark px-3 py-2 text-sm text-surface-mid"
          role="status"
        >
          view only — you can browse expenses but not add or edit them
        </p>

        <div
          class="flex w-full min-w-0 flex-col gap-3 md:flex-row md:items-center md:justify-between"
        >
          <AdminTabBar
            flush
            panel-id-prefix="expenses-tab"
            :model-value="activeTab"
            :tabs="expenseTabItems"
            @update:model-value="switchTab"
          />
          <div v-if="activeTab === 'transactions'" class="flex min-w-0 flex-wrap items-center gap-2">
            <SearchInput
              v-model="productFilter"
              class="w-full min-w-[12rem] max-w-xs"
              placeholder="filter by product"
              aria-label="filter by product"
              :min-length="1"
            />
            <ToolbarPillButton
              family="1xx"
              :selected="filtersOpen"
              :aria-expanded="filtersOpen"
              aria-controls="expense-transaction-filters"
              @click="filtersOpen = !filtersOpen"
            >
              <FilterIcon class-name="size-3.5" />
              {{ transactionFilterLabel }}
            </ToolbarPillButton>
            <ToolbarPillButton family="1xx" :disabled="exporting" @click="exportCsv">
              {{ exporting ? "exporting…" : "export csv" }}
            </ToolbarPillButton>
            <ToolbarPillButton v-if="canWriteExpenses" family="2xx" @click="openCreate">
              + expense
            </ToolbarPillButton>
          </div>
        </div>

        <ExpenseLedgerHeader
          v-if="showLedgerHeader"
          v-model:month-preset="monthPreset"
          v-model:date-filter-mode="dateFilterMode"
          v-model:selected-month="selectedMonth"
          v-model:date-from="dateFrom"
          v-model:date-to="dateTo"
          :month-label="monthLabel"
          :has-active-filters="hasActiveFilters"
          :range-error="rangeError"
          :summary="summary"
          :expense-categories="expenseCategories"
          :period-change="periodChange"
          :format-money="formatMoney"
          :summary-error="summaryError"
          :rates-error="ratesError"
          @apply-preset="handleDatePreset"
          @clear-filters="clearFilters"
          @retry="retrySummaryAndRates"
        />

        <ExpenseTransactionsPanel
          v-if="activeTab === 'transactions'"
          ref="transactionsPanelRef"
          v-model:product-filter="productFilter"
          v-model:category-filter="categoryFilter"
          v-model:display-currency="displayCurrency"
          v-model:smart-text-open="smartTextOpen"
          v-model:filters-open="filtersOpen"
          v-model:quick-add-category="quickAdd.category"
          v-model:quick-add-product="quickAdd.product"
          v-model:quick-add-price="quickAdd.price"
          :can-write="canWriteExpenses"
          :saving-expense="savingExpense"
          :category-options="categoryOptions"
          :product-suggestions="productSuggestions"
          :list-error="listError"
          :expenses="expenses"
          :list-loading="listLoading"
          :sort-indicator="sortIndicator"
          :sort-aria-sort="sortAriaSort"
          :month-label="monthLabel"
          :exchange-rates="exchangeRates"
          :format-money="formatMoney"
          :format-expense-date="formatExpenseDate"
          :convert-amount="convertAmount"
          :expense-total="expenseTotal"
          :expense-page="expensePage"
          :expense-pages="expensePages"
          :has-next-expense-page="hasNextExpensePage"
          :has-previous-expense-page="hasPreviousExpensePage"
          @submit-quick="quickSaveExpense"
          @smart-submit="saveSmartExpense"
          @clear-transaction-filters="clearTransactionFilters"
          @retry-list="goToExpensePage(expensePage)"
          @edit="openEdit"
          @delete="requestDeleteExpense"
          @duplicate="duplicateExpense"
          @sort="handleExpenseSort"
          @smart-text="openSmartText"
          @first-page="goToExpensePage(1)"
          @prev-page="goToExpensePage(expensePage - 1)"
          @next-page="goToExpensePage(expensePage + 1)"
          @last-page="goToExpensePage(expensePages)"
        />

        <section
          v-else-if="activeTab === 'insights'"
          id="expenses-tab-panel-insights"
          role="tabpanel"
          aria-labelledby="expenses-tab-tab-insights"
          tabindex="0"
          class="outline-none"
        >
          <ExpenseInsights
            :has-chart-data="hasChartData"
            :line-chart="lineChart"
            :bar-chart="barChart"
            :doughnut-chart="doughnutChart"
            :summary="summary"
            :expense-categories="expenseCategories"
            :format-money="formatMoney"
            @add-expense="goToTransactions"
          />
        </section>

        <ExpenseCalculatorTab v-else-if="activeTab === 'calculator'" />

        <section
          v-else-if="activeTab === 'settings'"
          id="expenses-tab-panel-settings"
          role="tabpanel"
          aria-labelledby="expenses-tab-tab-settings"
          tabindex="0"
          class="outline-none"
        >
          <ExpenseCategorySettings
            v-model:new-category-name="newCategoryName"
            v-model:editing-category-name="editingCategoryName"
            v-model:editing-category-budget="editingCategoryBudget"
            :expense-categories="expenseCategories"
            :editing-category-id="editingCategoryId"
            :exchange-rates="exchangeRates"
            @add-category="addCategory"
            @start-edit-category="startEditCategory"
            @cancel-edit-category="cancelEditCategory"
            @save-category-rename="saveCategoryRename"
            @remove-category="requestDeleteCategory"
          />
        </section>
      </div>

      <ExpenseFormDrawer
        v-if="canWriteExpenses"
        v-model:category="form.category"
        v-model:tool-name="form.tool_name"
        v-model:amount="form.amount"
        v-model:currency="form.currency"
        v-model:expense-date="form.expense_date"
        v-model:notes="form.notes"
        :open="showForm"
        :loading="savingExpense"
        :title="formTitle"
        :category-options="categoryOptions"
        @submit="saveExpense"
        @close="showForm = false"
      />

      <ConfirmDialog
        v-if="canWriteExpenses"
        :open="deleteTargetId !== null"
        title="delete expense"
        message="This expense will be permanently removed."
        confirm-label="delete"
        :loading="deletingExpense"
        danger
        @confirm="confirmDeleteExpense"
        @cancel="deleteTargetId = null"
      />

      <ConfirmDialog
        v-if="canWriteExpenses"
        :open="deleteCategoryTarget !== null"
        title="delete category"
        :message="deleteCategoryTarget ? `delete category '${deleteCategoryTarget.name}'?` : ''"
        confirm-label="delete"
        :loading="deletingCategory"
        danger
        @confirm="confirmDeleteCategory"
        @cancel="deleteCategoryTarget = null"
      />
    </div>
  </AdminPageLayout>
</template>
