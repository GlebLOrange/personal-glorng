<script setup lang="ts">
import { computed, defineAsyncComponent, nextTick, useTemplateRef } from "vue";

import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import ExpenseDashboardPanel from "@/components/expenses/ExpenseDashboardPanel.vue";
import ExpenseFormDrawer from "@/components/expenses/ExpenseFormDrawer.vue";
import ExpenseTransactionsPanel from "@/components/expenses/ExpenseTransactionsPanel.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { Card } from "@/components/ui/card";
import { useExpensesTool, type ExpenseQuickAddTarget } from "@/composables/useExpensesTool";
import { usePermissions } from "@/composables/usePermissions";

const ExpenseCalculatorTab = defineAsyncComponent(
  () => import("@/components/expenses/ExpenseCalculatorTab.vue"),
);
const ExpenseCategorySettings = defineAsyncComponent(
  () => import("@/components/expenses/ExpenseCategorySettings.vue"),
);
const ExpenseInsights = defineAsyncComponent(
  () => import("@/components/expenses/ExpenseInsights.vue"),
);

const dashboardPanelRef = useTemplateRef<ExpenseQuickAddTarget>("dashboardPanelRef");

const {
  activeTab,
  expenseTabItems,
  converterMounted,
  savingExpense,
  exporting,
  deletingExpense,
  deletingCategory,
  smartTextOpen,
  showForm,
  deleteTargetId,
  deleteCategoryTarget,
  deleteCategoryReplacementId,
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

const deleteCategoryOptions = computed(() =>
  expenseCategories.value.filter((c) => c.id !== deleteCategoryTarget.value?.id),
);

function retrySummaryAndRates(): void {
  void Promise.all([loadSummary(), loadRates()]);
}

function focusAddFromInsights(): void {
  switchTab("today");
  void nextTick(() => {
    dashboardPanelRef.value?.focusEntry();
  });
}
</script>

<template>
  <PageShell
    title="expenses"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'expenses' }]"
    back-to="/tools"
    max-width="5xl"
    :narrow="false"
  >
    <div class="min-w-0">
      <div class="flex flex-col gap-3">
        <p
          v-if="!canWriteExpenses"
          class="rounded-lg bg-surface-dark px-3 py-2 text-sm text-surface-mid"
          role="status"
        >
          view only — you can browse expenses but not add or edit them
        </p>

        <div class="border-b border-surface-border/50 pb-3">
          <AdminTabBar
            flush
            panel-id-prefix="expenses-tab"
            :model-value="activeTab"
            :tabs="expenseTabItems"
            aria-label="expense sections"
            @update:model-value="switchTab"
          >
            <template #end>
              <ToolbarPillButton action="save" :disabled="exporting" @click="exportCsv">
                {{ exporting ? "exporting…" : "export csv" }}
              </ToolbarPillButton>
            </template>
          </AdminTabBar>
        </div>

        <ExpenseDashboardPanel
          v-show="activeTab === 'today'"
          ref="dashboardPanelRef"
          v-model:smart-text-open="smartTextOpen"
          v-model:quick-add-category="quickAdd.category"
          v-model:quick-add-product="quickAdd.product"
          v-model:quick-add-price="quickAdd.price"
          v-model:quick-add-expense-date="quickAdd.expense_date"
          v-model:quick-add-name-error="quickAddNameError"
          v-model:quick-add-amount-error="quickAddAmountError"
          v-model:display-currency="displayCurrency"
          :aria-hidden="activeTab !== 'today'"
          :can-write="canWriteExpenses"
          :saving-expense="savingExpense"
          :category-options="categoryOptions"
          :product-suggestions="productSuggestions"
          :month-label="monthLabel"
          :summary="summary"
          :summary-error="summaryError"
          :rates-error="ratesError"
          :expense-total="expenseTotal"
          :expenses="expenses"
          :format-money="formatMoney"
          :format-expense-date="formatExpenseDate"
          @retry-summary="retrySummaryAndRates"
          @submit-quick="quickSaveExpense"
          @smart-submit="saveSmartExpense"
          @open-activity="switchTab('activity')"
        />

        <ExpenseTransactionsPanel
          v-show="activeTab === 'activity'"
          v-model:product-filter="productFilter"
          v-model:category-filter="categoryFilter"
          v-model:display-currency="displayCurrency"
          v-model:month-preset="monthPreset"
          v-model:date-filter-mode="dateFilterMode"
          v-model:selected-month="selectedMonth"
          v-model:date-from="dateFrom"
          v-model:date-to="dateTo"
          :aria-hidden="activeTab !== 'activity'"
          :category-options="categoryOptions"
          :list-error="listError"
          :expenses="expenses"
          :list-loading="listLoading"
          :sort-indicator="sortIndicator"
          :sort-aria-sort="sortAriaSort"
          :month-label="monthLabel"
          :has-active-filters="hasActiveFilters"
          :range-error="rangeError"
          :exchange-rates="exchangeRates"
          :format-money="formatMoney"
          :format-expense-date="formatExpenseDate"
          :convert-amount="convertAmount"
          :expense-total="expenseTotal"
          :expense-page="expensePage"
          :expense-pages="expensePages"
          :has-next-expense-page="hasNextExpensePage"
          :has-previous-expense-page="hasPreviousExpensePage"
          @apply-preset="handleDatePreset"
          @clear-filters="clearFilters"
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
          v-show="activeTab === 'insights'"
          id="expenses-tab-panel-insights"
          role="tabpanel"
          aria-labelledby="expenses-tab-tab-insights"
          :aria-hidden="activeTab !== 'insights'"
          tabindex="0"
          class="outline-none"
        >
          <ExpenseInsights
            :has-chart-data="hasChartData"
            :line-chart="lineChart"
            :bar-chart="barChart"
            :doughnut-chart="doughnutChart"
            :summary="summary"
            :format-money="formatMoney"
            @add-expense="focusAddFromInsights"
          />
        </section>

        <section
          v-show="activeTab === 'categories'"
          id="expenses-tab-panel-categories"
          role="tabpanel"
          aria-labelledby="expenses-tab-tab-categories"
          :aria-hidden="activeTab !== 'categories'"
          tabindex="0"
          class="outline-none"
        >
          <div class="flex flex-col gap-3">
            <Card
              v-if="canWriteExpenses"
              variant="compact"
              class="flex min-w-0 flex-wrap items-end gap-2"
            >
              <form
                class="flex min-w-0 flex-1 flex-wrap items-end gap-2"
                @submit.prevent="addCategory"
              >
                <BaseInput
                  v-model="newCategoryName"
                  placeholder="title"
                  aria-label="title"
                  class="min-w-0 flex-1"
                />
                <ToolbarPillButton type="submit" action="save" class="shrink-0">
                  + category
                </ToolbarPillButton>
              </form>
            </Card>
            <ExpenseCategorySettings
              v-model:editing-category-name="editingCategoryName"
              :expense-categories="expenseCategories"
              :editing-category-id="editingCategoryId"
              @start-edit-category="startEditCategory"
              @cancel-edit-category="cancelEditCategory"
              @save-category-rename="saveCategoryRename"
              @remove-category="requestDeleteCategory"
            />
          </div>
        </section>

        <section
          v-show="activeTab === 'converter'"
          id="expenses-tab-panel-converter"
          role="tabpanel"
          aria-labelledby="expenses-tab-tab-converter"
          :aria-hidden="activeTab !== 'converter'"
          tabindex="0"
          class="outline-none"
        >
          <ExpenseCalculatorTab v-if="converterMounted" />
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
        confirm-label="delete"
        :loading="deletingCategory"
        danger
        @confirm="confirmDeleteCategory"
        @cancel="deleteCategoryTarget = null"
      >
        <div class="flex flex-col gap-3">
          <p>
            delete category '{{ deleteCategoryTarget?.name }}'? Expenses in this category will move
            to the destination below.
          </p>
          <BaseSelect
            :model-value="
              deleteCategoryReplacementId === null || deleteCategoryReplacementId === undefined
                ? ''
                : String(deleteCategoryReplacementId)
            "
            label="move expenses to"
            aria-label="replacement category"
            @update:model-value="
              deleteCategoryReplacementId = $event === '' ? null : Number($event)
            "
          >
            <option value="">Uncategorized</option>
            <option v-for="cat in deleteCategoryOptions" :key="cat.id" :value="String(cat.id)">
              {{ cat.name }}
            </option>
          </BaseSelect>
        </div>
      </ConfirmDialog>
    </div>
  </PageShell>
</template>
