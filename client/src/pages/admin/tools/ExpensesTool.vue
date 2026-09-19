<script setup lang="ts">
import { computed, defineAsyncComponent, ref, useTemplateRef, watch } from "vue";

import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import ExpenseDashboardPanel from "@/components/expenses/ExpenseDashboardPanel.vue";
import ExpenseFormDrawer from "@/components/expenses/ExpenseFormDrawer.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import {
  useExpensesTool,
  type ExpenseQuickAddTarget,
} from "@/composables/useExpensesTool";
import { usePermissions } from "@/composables/usePermissions";

const ExpenseCalculatorTab = defineAsyncComponent(
  () => import("@/components/expenses/ExpenseCalculatorTab.vue"),
);
const ExpenseCategorySettings = defineAsyncComponent(
  () => import("@/components/expenses/ExpenseCategorySettings.vue"),
);

const dashboardPanelRef = useTemplateRef<ExpenseQuickAddTarget>("dashboardPanelRef");

const {
  activeTab,
  expenseTabItems,
  savingExpense,
  exporting,
  deletingExpense,
  deletingCategory,
  smartTextOpen,
  showForm,
  deleteTargetId,
  deleteCategoryTarget,
  expensePage,
  displayCurrency,
  expenses,
  expensePages,
  summary,
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
  quickAddNameError,
  quickAddAmountError,
  form,
  formTitle,
  expenseTotal,
  hasPreviousExpensePage,
  hasNextExpensePage,
  productSuggestions,
  sortIndicator,
  sortAriaSort,
  handleDatePreset,
  clearTransactionFilters,
  goToExpensePage,
  handleExpenseSort,
  openEdit,
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
} = useExpensesTool(dashboardPanelRef);

const { can } = usePermissions();
const canWriteExpenses = computed(() => can("expenses", "write"));

/** Keep converter mounted after first visit so amount/pair survive tab switches. */
const converterMounted = ref(false);
watch(
  activeTab,
  (tab) => {
    if (tab === "converter") converterMounted.value = true;
  },
  { immediate: true },
);

function retrySummaryAndRates(): void {
  void Promise.all([loadSummary(), loadRates()]);
}

function openSettings(): void {
  switchTab("categories");
}
</script>

<template>
  <AdminPageLayout hub="tools" title="expenses" max-width="xl">
    <div class="min-w-0">
      <div class="flex flex-col gap-4">
        <p
          v-if="!canWriteExpenses"
          class="rounded-lg bg-surface-dark px-3 py-2 text-sm text-surface-mid"
          role="status"
        >
          view only — you can browse expenses but not add or edit them
        </p>

        <AdminTabBar
          flush
          panel-id-prefix="expenses-tab"
          :model-value="activeTab"
          :tabs="expenseTabItems"
          aria-label="expense sections"
          @update:model-value="switchTab"
        />

        <form
          v-if="activeTab === 'categories' && canWriteExpenses"
          class="flex min-w-0 flex-wrap items-center gap-2"
          @submit.prevent="addCategory"
        >
          <BaseInput
            v-model="newCategoryName"
            placeholder="category"
            aria-label="category"
            class="min-w-0 flex-1"
          />
          <ToolbarPillButton type="submit" family="2xx" class="shrink-0">
            + category
          </ToolbarPillButton>
        </form>

        <ExpenseDashboardPanel
          v-show="activeTab === 'expenses'"
          :aria-hidden="activeTab !== 'expenses'"
          ref="dashboardPanelRef"
          v-model:month-preset="monthPreset"
          v-model:date-filter-mode="dateFilterMode"
          v-model:selected-month="selectedMonth"
          v-model:date-from="dateFrom"
          v-model:date-to="dateTo"
          v-model:product-filter="productFilter"
          v-model:category-filter="categoryFilter"
          v-model:display-currency="displayCurrency"
          v-model:smart-text-open="smartTextOpen"
          v-model:quick-add-category="quickAdd.category"
          v-model:quick-add-product="quickAdd.product"
          v-model:quick-add-price="quickAdd.price"
          v-model:quick-add-expense-date="quickAdd.expense_date"
          v-model:quick-add-name-error="quickAddNameError"
          v-model:quick-add-amount-error="quickAddAmountError"
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
          :has-active-filters="hasActiveFilters"
          :range-error="rangeError"
          :summary="summary"
          :expense-categories="expenseCategories"
          :summary-error="summaryError"
          :rates-error="ratesError"
          :exchange-rates="exchangeRates"
          :format-money="formatMoney"
          :format-expense-date="formatExpenseDate"
          :convert-amount="convertAmount"
          :expense-total="expenseTotal"
          :expense-page="expensePage"
          :expense-pages="expensePages"
          :has-next-expense-page="hasNextExpensePage"
          :has-previous-expense-page="hasPreviousExpensePage"
          :has-chart-data="hasChartData"
          :line-chart="lineChart"
          :bar-chart="barChart"
          :doughnut-chart="doughnutChart"
          @apply-preset="handleDatePreset"
          @clear-filters="clearFilters"
          @retry-summary="retrySummaryAndRates"
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

        <ExpenseCalculatorTab
          v-if="converterMounted"
          v-show="activeTab === 'converter'"
          :aria-hidden="activeTab !== 'converter'"
        />

        <section
          v-if="activeTab === 'categories'"
          id="expenses-tab-panel-categories"
          role="tabpanel"
          aria-labelledby="expenses-tab-tab-categories"
          tabindex="0"
          class="outline-none"
        >
          <ExpenseCategorySettings
            v-model:editing-category-name="editingCategoryName"
            :expense-categories="expenseCategories"
            :editing-category-id="editingCategoryId"
            @start-edit-category="startEditCategory"
            @cancel-edit-category="cancelEditCategory"
            @save-category-rename="saveCategoryRename"
            @remove-category="requestDeleteCategory"
          />
        </section>

        <footer
          v-if="activeTab === 'expenses'"
          class="flex flex-wrap items-center justify-between gap-2 border-t border-surface-border/60 pt-4"
        >
          <ToolbarPillButton family="1xx" :disabled="exporting" @click="exportCsv">
            {{ exporting ? "exporting…" : "export csv" }}
          </ToolbarPillButton>
          <ToolbarPillButton family="1xx" @click="openSettings">
            settings
          </ToolbarPillButton>
        </footer>
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
