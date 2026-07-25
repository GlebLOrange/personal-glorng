<script setup lang="ts">
import ExpenseDateFilters from "@/components/expenses/ExpenseDateFilters.vue";
import ExpenseSummaryCard from "@/components/expenses/ExpenseSummaryCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import type { DateFilterMode, MonthPreset } from "@/composables/useExpenseFilters";
import type { ExpenseCategory, ExpenseSummary } from "@/types";

const monthPreset = defineModel<MonthPreset>("monthPreset", { required: true });
const dateFilterMode = defineModel<DateFilterMode>("dateFilterMode", { required: true });
const selectedMonth = defineModel<string>("selectedMonth", { required: true });
const dateFrom = defineModel<string>("dateFrom", { required: true });
const dateTo = defineModel<string>("dateTo", { required: true });

defineProps<{
  monthLabel: string;
  hasActiveFilters: boolean;
  rangeError: string | null;
  summary: ExpenseSummary | null;
  expenseCategories: ExpenseCategory[];
  periodChange: { delta: number; increased: boolean } | null;
  formatMoney: (amount: string | number, currency: string) => string;
  summaryError: string | null;
  ratesError: string | null;
}>();

const emit = defineEmits<{
  applyPreset: [preset: MonthPreset];
  clearFilters: [];
  retry: [];
}>();
</script>

<template>
  <section class="mb-4 flex flex-col gap-3">
    <Card variant="compact" class="flex flex-col gap-3">
      <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="text-xs text-surface-mid">period</p>
          <p class="text-lg font-semibold text-surface-light">{{ monthLabel }}</p>
        </div>
        <ExpenseDateFilters
          v-model:month-preset="monthPreset"
          v-model:date-filter-mode="dateFilterMode"
          v-model:selected-month="selectedMonth"
          v-model:date-from="dateFrom"
          v-model:date-to="dateTo"
          :has-active-filters="hasActiveFilters"
          @apply-preset="emit('applyPreset', $event)"
          @clear-filters="emit('clearFilters')"
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
    <div
      v-if="summaryError || ratesError"
      class="alert-surface-error flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"
      role="alert"
    >
      <span>{{ summaryError || ratesError }}</span>
      <BaseButton variant="ghost" size="sm" @click="emit('retry')">retry</BaseButton>
    </div>
  </section>
</template>
