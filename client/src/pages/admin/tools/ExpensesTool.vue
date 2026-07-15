<script setup lang="ts">
import { computed, defineAsyncComponent, useTemplateRef } from "vue";

import ExpenseCalculatorBudget from "@/components/expense-calculator/ExpenseCalculatorBudget.vue";
import ExpenseCalculatorConvert from "@/components/expense-calculator/ExpenseCalculatorConvert.vue";
import ExpenseCalculatorLineItems from "@/components/expense-calculator/ExpenseCalculatorLineItems.vue";
import ExpenseCalculatorWhatIf from "@/components/expense-calculator/ExpenseCalculatorWhatIf.vue";
import ExpenseCategoryChips from "@/components/expenses/ExpenseCategoryChips.vue";
import ExpenseCategorySettings from "@/components/expenses/ExpenseCategorySettings.vue";
import ExpenseConfirmDialog from "@/components/expenses/ExpenseConfirmDialog.vue";
import ExpenseDateFilters from "@/components/expenses/ExpenseDateFilters.vue";
import ExpenseFormModal from "@/components/expenses/ExpenseFormModal.vue";
import ExpenseList from "@/components/expenses/ExpenseList.vue";
import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";
import ExpenseSummaryCard from "@/components/expenses/ExpenseSummaryCard.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import { Card } from "@/components/ui/card";
import { useExpenseCalculator } from "@/composables/useExpenseCalculator";
import { isCalculatorTab, useExpensesTool } from "@/composables/useExpensesTool";
import type { CurrencyCode } from "@/composables/useExpenseFilters";

const ExpenseInsights = defineAsyncComponent(
  () => import("@/components/expenses/ExpenseInsights.vue"),
);

const quickAddRef = useTemplateRef<InstanceType<typeof ExpenseQuickAdd>>("quickAddRef");

const {
  activeTab,
  expenseTabItems,
  loading,
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
  smartText,
  quickAddCurrency,
  parsed,
  parsing,
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
  duplicateExpense,
  exportCsv,
  requestDeleteExpense,
  confirmDeleteExpense,
  requestDeleteCategory,
  confirmDeleteCategory,
  switchTab,
  saveExpense,
  quickSaveExpense,
} = useExpensesTool(quickAddRef);

const {
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

const showCalculatorChrome = computed(() => isCalculatorTab(activeTab.value));

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
  <AdminPageLayout title="expenses" max-width="xl">
    <div class="min-w-0">
    <section v-if="showLedgerHeader" class="mb-6 flex flex-col gap-4">
      <Card variant="compact" class="flex flex-col gap-3">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div>
            <p class="text-xs text-surface-mid uppercase tracking-wider">Period</p>
            <p class="text-surface-light text-lg font-semibold">{{ monthLabel }}</p>
          </div>
          <ExpenseDateFilters
            v-model:month-preset="monthPreset"
            v-model:date-filter-mode="dateFilterMode"
            v-model:selected-month="selectedMonth"
            v-model:date-from="dateFrom"
            v-model:date-to="dateTo"
            :has-active-filters="hasActiveFilters"
            @apply-preset="handleDatePreset"
            @clear-filters="clearFilters"
          />
        </div>
        <p v-if="rangeError" class="text-sm text-status-error" role="alert">
          {{ rangeError }}
        </p>
      </Card>

      <ExpenseSummaryCard
        :summary="summary"
        :month-label="monthLabel"
        :expense-categories="expenseCategories"
        :period-change="periodChange"
        :format-money="formatMoney"
      />
      <div v-if="summaryError || ratesError" class="alert-surface-error" role="alert">
        {{ summaryError || ratesError }}
      </div>
    </section>

    <AdminTabBar
      panel-id-prefix="expenses-tab"
      :model-value="activeTab"
      :tabs="expenseTabItems"
      @update:model-value="switchTab"
    />

    <section
      v-if="showCalculatorChrome"
      class="mb-6 flex flex-col gap-4"
    >
      <Card variant="compact" class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <p class="text-sm text-surface-mid">{{ persistenceHint }}</p>
        <div v-if="isSuperuser" class="flex flex-wrap gap-2">
          <BaseButton variant="ghost" size="sm" :disabled="loadingState" @click="loadState">
            {{ loadingState ? "loading..." : "load" }}
          </BaseButton>
          <BaseButton variant="primary" size="sm" :disabled="saving || !stateDirty" @click="saveState">
            {{ saving ? "saving..." : "save" }}
          </BaseButton>
        </div>
      </Card>

      <div class="md:w-36">
        <select
          v-model="calculatorDisplayCurrency"
          aria-label="display currency"
          class="w-full bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue h-[42px]"
        >
          <option value="PLN">PLN</option>
          <option value="EUR">EUR</option>
          <option value="USD">USD</option>
          <option value="BYN">BYN</option>
        </select>
      </div>
    </section>

    <section
      v-if="activeTab === 'transactions'"
      id="expenses-tab-panel-transactions"
      role="tabpanel"
      aria-labelledby="expenses-tab-tab-transactions"
      tabindex="0"
      class="flex flex-col gap-4 outline-none"
    >
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <h2 class="text-lg font-semibold text-surface-light">transactions</h2>
        <div class="flex flex-wrap gap-2">
          <BaseButton
            variant="ghost"
            :disabled="loading"
            :aria-expanded="filtersOpen"
            aria-controls="expense-transaction-filters"
            @click="filtersOpen = !filtersOpen"
          >
            {{ transactionFilterLabel }}
          </BaseButton>
          <BaseButton variant="ghost" :disabled="loading" @click="exportCsv">export csv</BaseButton>
          <BaseButton variant="primary" @click="openCreate">+ add</BaseButton>
        </div>
      </div>

      <ExpenseQuickAdd
        ref="quickAddRef"
        v-model:smart-text="smartText"
        v-model:category="quickAdd.category"
        v-model:product="quickAdd.product"
        v-model:price="quickAdd.price"
        :loading="loading"
        :parsing="parsing"
        :parsed="parsed"
        :category-options="categoryOptions"
        :product-suggestions="productSuggestions"
        :currency-label="quickAddCurrency"
        @submit="quickSaveExpense"
      />

      <Card
        v-if="filtersOpen"
        id="expense-transaction-filters"
        variant="compact"
        class="flex flex-col gap-4"
      >
        <div class="flex flex-col md:flex-row md:items-end gap-3">
          <div class="flex-1">
            <BaseInput v-model="productFilter" placeholder="filter by product..." />
          </div>
          <BaseButton
            v-if="productFilter || categoryFilter"
            variant="ghost"
            @click="clearTransactionFilters"
          >
            clear transaction filters
          </BaseButton>
        </div>

        <ExpenseCategoryChips
          v-model:category-filter="categoryFilter"
          :category-options="categoryOptions"
        />
      </Card>

      <ErrorState
        v-if="listError"
        :message="listError"
        show-retry
        @retry="goToExpensePage(expensePage)"
      />

      <ExpenseList
        :expenses="expenses"
        :loading="listLoading"
        :sort-indicator="sortIndicator"
        :sort-aria-sort="sortAriaSort"
        :month-label="monthLabel"
        :display-currency="displayCurrency as CurrencyCode"
        :exchange-rates="exchangeRates"
        :format-money="formatMoney"
        :format-expense-date="formatExpenseDate"
        :convert-amount="convertAmount"
        @edit="openEdit"
        @delete="requestDeleteExpense"
        @duplicate="duplicateExpense"
        @sort="handleExpenseSort"
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
        @prev="goToExpensePage(expensePage - 1)"
        @next="goToExpensePage(expensePage + 1)"
      />
    </section>

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
      />
    </section>

    <section
      v-else-if="activeTab === 'convert'"
      id="expenses-tab-panel-convert"
      role="tabpanel"
      aria-labelledby="expenses-tab-tab-convert"
      tabindex="0"
      class="outline-none"
    >
      <ExpenseCalculatorConvert :exchange-rates="calculatorRates" :rates-loading="ratesLoading" />
    </section>

    <section
      v-else-if="activeTab === 'sum'"
      id="expenses-tab-panel-sum"
      role="tabpanel"
      aria-labelledby="expenses-tab-tab-sum"
      tabindex="0"
      class="outline-none"
    >
      <ExpenseCalculatorLineItems
        :line-items="lineItems"
        :display-currency="calculatorDisplayCurrency"
        :sum-total="sumTotal"
        :format-money="formatCalculatorMoney"
        @add="addLineItem"
        @remove="removeLineItem"
        @apply-to-budget="applySumToBudget"
      />
    </section>

    <section
      v-else-if="activeTab === 'budget'"
      id="expenses-tab-panel-budget"
      role="tabpanel"
      aria-labelledby="expenses-tab-tab-budget"
      tabindex="0"
      class="outline-none"
    >
      <ExpenseCalculatorBudget
        :budget-rows="budgetRows"
        :budget-summary="budgetSummary"
        :display-currency="calculatorDisplayCurrency"
        :format-money="formatCalculatorMoney"
        @add="addBudgetRow"
        @remove="removeBudgetRow"
      />
    </section>

    <section
      v-else-if="activeTab === 'whatif'"
      id="expenses-tab-panel-whatif"
      role="tabpanel"
      aria-labelledby="expenses-tab-tab-whatif"
      tabindex="0"
      class="outline-none"
    >
      <ExpenseCalculatorWhatIf
        v-model:what-if-category-id="whatIfCategoryId"
        v-model:what-if-amount="whatIfAmount"
        v-model:what-if-currency="whatIfCurrency"
        :budget-options="budgetOptions"
        :display-currency="calculatorDisplayCurrency"
        :projection="whatIfProjection"
        :format-money="formatCalculatorMoney"
      />
    </section>

    <section
      v-else-if="activeTab === 'settings'"
      id="expenses-tab-panel-settings"
      role="tabpanel"
      aria-labelledby="expenses-tab-tab-settings"
      tabindex="0"
      class="outline-none"
    >
      <ExpenseCategorySettings
        v-model:display-currency="displayCurrency"
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

    <ExpenseFormModal
      v-model:category="form.category"
      v-model:tool-name="form.tool_name"
      v-model:amount="form.amount"
      v-model:currency="form.currency"
      v-model:expense-date="form.expense_date"
      v-model:notes="form.notes"
      :open="showForm"
      :loading="loading"
      :title="formTitle"
      :category-options="categoryOptions"
      @submit="saveExpense"
      @close="showForm = false"
    />

    <ExpenseConfirmDialog
      :open="deleteTargetId !== null"
      title="delete expense"
      message="This expense will be permanently removed."
      confirm-label="delete"
      :loading="loading"
      @confirm="confirmDeleteExpense"
      @cancel="deleteTargetId = null"
    />

    <ExpenseConfirmDialog
      :open="deleteCategoryTarget !== null"
      title="delete category"
      :message="deleteCategoryTarget ? `delete category '${deleteCategoryTarget.name}'?` : ''"
      confirm-label="delete"
      :loading="loading"
      @confirm="confirmDeleteCategory"
      @cancel="deleteCategoryTarget = null"
    />
    </div>
  </AdminPageLayout>
</template>
