<script setup lang="ts">
import ExpenseDateFilters from "@/components/expenses/ExpenseDateFilters.vue";
import ExpenseSummaryCard from "@/components/expenses/ExpenseSummaryCard.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import type { DateFilterMode, MonthPreset } from "@/composables/useExpenseFilters";
import type { ExpenseSummary } from "@/types";

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
  expenseTotal: number;
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
  <section class="flex flex-col gap-4" aria-label="expense period summary">
    <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
      <div class="min-w-0 shrink-0">
        <h2 class="text-base font-semibold text-surface-light">Expenses</h2>
        <p class="text-xs text-surface-mid">{{ monthLabel }}</p>
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

    <ExpenseSummaryCard
      :summary="summary"
      :expense-total="expenseTotal"
      :format-money="formatMoney"
    />

    <p v-if="rangeError" class="text-sm text-status-error" role="alert">
      {{ rangeError }}
    </p>

    <div
      v-if="summaryError || ratesError"
      class="alert-surface-error flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"
      role="alert"
    >
      <span>{{ summaryError || ratesError }}</span>
      <BaseButton variant="ghost" size="sm" class="gap-1.5" @click="emit('retry')">
        <RefreshIcon class-name="size-3.5" />
        retry
      </BaseButton>
    </div>
  </section>
</template>
