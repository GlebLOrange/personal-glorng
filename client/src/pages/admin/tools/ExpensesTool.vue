<script setup lang="ts">
import { computed, defineAsyncComponent, useTemplateRef } from "vue";

import ExpenseCategorySettings from "@/components/expenses/ExpenseCategorySettings.vue";
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import ExpenseCalculatorPanel from "@/components/expenses/ExpenseCalculatorPanel.vue";
import ExpenseFormDrawer from "@/components/expenses/ExpenseFormDrawer.vue";
import ExpenseLedgerHeader from "@/components/expenses/ExpenseLedgerHeader.vue";
import ExpenseTransactionsPanel from "@/components/expenses/ExpenseTransactionsPanel.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import FilterIcon from "@/components/icons/FilterIcon.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { useExpenseCalculator } from "@/composables/useExpenseCalculator";
import {
  isCalculatorTab,
  useExpensesTool,
  type ExpenseQuickAddTarget,
} from "@/composables/useExpensesTool";
import { buildPersistenceHint } from "@/utils/expensePersistenceHint";

const ExpenseInsights = defineAsyncComponent(
  () => import("@/components/expenses/ExpenseInsights.vue"),
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

const {
  activeMode,
  modeTabs,
  switchMode,
  exchangeRates: calculatorRates,
  ratesLoading,
  displayCurrency: calculatorDisplayCurrency,
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
  formatMoney: formatCalculatorMoney,
  addLineItem,
  removeLineItem,
  addBudgetRow,
  removeBudgetRow,
  applySumToBudget,
  saveState,
  loadState,
} = useExpenseCalculator();

const showLedgerHeader = computed(() => !isCalculatorTab(activeTab.value));

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

function retrySummaryAndRates(): void {
  void Promise.all([loadSummary(), loadRates()]);
}

function goToBudgetMode(): void {
  switchMode("budget");
}

function goToTransactions(): void {
  switchTab("transactions");
}
</script>

<template>
  <AdminPageLayout hub="tools" title="expenses" max-width="xl">
    <div class="min-w-0">
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

      <div class="flex flex-col gap-3">
        <div class="flex w-full min-w-0 flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <AdminTabBar
            flush
            panel-id-prefix="expenses-tab"
            :model-value="activeTab"
            :tabs="expenseTabItems"
            @update:model-value="switchTab"
          />
          <div v-if="activeTab === 'transactions'" class="flex flex-wrap gap-2">
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
              {{ exporting ? "exporting..." : "export csv" }}
            </ToolbarPillButton>
            <ToolbarPillButton family="2xx" @click="openCreate">
              + expense
            </ToolbarPillButton>
          </div>
        </div>

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

        <ExpenseCalculatorPanel
          v-else-if="activeTab === 'calculator'"
          v-model:display-currency="calculatorDisplayCurrency"
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
          :exchange-rates="calculatorRates"
          :rates-loading="ratesLoading"
          :line-items="lineItems"
          :sum-total="sumTotal"
          :budget-rows="budgetRows"
          :budget-summary="budgetSummary"
          :budget-options="budgetOptions"
          :what-if-projection="whatIfProjection"
          :format-money="formatCalculatorMoney"
          @load-state="loadState"
          @save-state="saveState"
          @change-mode="switchMode"
          @add-line-item="addLineItem"
          @remove-line-item="removeLineItem"
          @apply-sum-to-budget="applySumToBudget"
          @add-budget-row="addBudgetRow"
          @remove-budget-row="removeBudgetRow"
          @go-to-budget="goToBudgetMode"
        />

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
