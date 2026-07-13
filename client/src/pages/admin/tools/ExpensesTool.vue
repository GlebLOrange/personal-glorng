<script setup lang="ts">
import { defineAsyncComponent, useTemplateRef } from "vue";

import ExpenseCategoryChips from "@/components/expenses/ExpenseCategoryChips.vue";
import ExpenseCategorySettings from "@/components/expenses/ExpenseCategorySettings.vue";
import ExpenseConfirmDialog from "@/components/expenses/ExpenseConfirmDialog.vue";
import ExpenseCurrencyConverter from "@/components/expenses/ExpenseCurrencyConverter.vue";
import ExpenseDateFilters from "@/components/expenses/ExpenseDateFilters.vue";
import ExpenseFormModal from "@/components/expenses/ExpenseFormModal.vue";
import ExpenseList from "@/components/expenses/ExpenseList.vue";
import ExpenseQuickAdd from "@/components/expenses/ExpenseQuickAdd.vue";
import ExpenseSummaryCard from "@/components/expenses/ExpenseSummaryCard.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { Card } from "@/components/ui/card";
import { useExpensesTool } from "@/composables/useExpensesTool";
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
  expenseCountLabel,
  hasPreviousExpensePage,
  hasNextExpensePage,
  transactionFilterLabel,
  productSuggestions,
  sortIndicator,
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
</script>

<template>
  <AdminPageLayout title="expenses" max-width="xl">
    <div class="min-w-0">
    <section class="mb-6 flex flex-col gap-4">
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

    <AdminTabBar :model-value="activeTab" :tabs="expenseTabItems" @update:model-value="switchTab" />

    <div v-if="activeTab === 'transactions'" class="flex flex-col gap-4">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold text-surface-light">Transactions</h2>
          <p class="text-xs text-surface-mid">{{ expenseCountLabel }}</p>
        </div>
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
          <BaseButton variant="ghost" :disabled="loading" @click="exportCsv">Export CSV</BaseButton>
          <BaseButton variant="primary" @click="openCreate">+ Add</BaseButton>
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
            <BaseInput v-model="productFilter" placeholder="Filter by product..." />
          </div>
          <BaseButton
            v-if="productFilter || categoryFilter"
            variant="ghost"
            @click="clearTransactionFilters"
          >
            Clear transaction filters
          </BaseButton>
        </div>

        <ExpenseCategoryChips
          v-model:category-filter="categoryFilter"
          :category-options="categoryOptions"
        />
      </Card>

      <div v-if="listError" class="alert-surface-error" role="alert">
        {{ listError }}
      </div>

      <ExpenseList
        :expenses="expenses"
        :loading="listLoading"
        :sort-indicator="sortIndicator"
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

      <div
        v-if="expensePages > 1"
        class="flex items-center justify-between gap-3 text-xs text-surface-mid"
      >
        <BaseButton
          variant="ghost"
          size="sm"
          :disabled="!hasPreviousExpensePage || listLoading"
          @click="goToExpensePage(expensePage - 1)"
        >
          Previous
        </BaseButton>
        <span>Page {{ expensePage }} of {{ expensePages }}</span>
        <BaseButton
          variant="ghost"
          size="sm"
          :disabled="!hasNextExpensePage || listLoading"
          @click="goToExpensePage(expensePage + 1)"
        >
          Next
        </BaseButton>
      </div>
    </div>

    <ExpenseInsights
      v-else-if="activeTab === 'insights'"
      :has-chart-data="hasChartData"
      :line-chart="lineChart"
      :bar-chart="barChart"
      :doughnut-chart="doughnutChart"
    />

    <ExpenseCurrencyConverter
      v-else-if="activeTab === 'converter'"
      :exchange-rates="exchangeRates"
    />

    <ExpenseCategorySettings
      v-else-if="activeTab === 'settings'"
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
      title="Delete expense"
      message="This expense will be permanently removed."
      confirm-label="Delete"
      :loading="loading"
      @confirm="confirmDeleteExpense"
      @cancel="deleteTargetId = null"
    />

    <ExpenseConfirmDialog
      :open="deleteCategoryTarget !== null"
      title="Delete category"
      :message="deleteCategoryTarget ? `Delete category '${deleteCategoryTarget.name}'?` : ''"
      confirm-label="Delete"
      :loading="loading"
      @confirm="confirmDeleteCategory"
      @cancel="deleteCategoryTarget = null"
    />
    </div>
  </AdminPageLayout>
</template>
