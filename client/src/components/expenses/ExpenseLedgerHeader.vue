<script setup lang="ts">
import ExpenseDateFilters from "@/components/expenses/ExpenseDateFilters.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { Card } from "@/components/ui/card";
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
  openTransactions: [];
}>();
</script>

<template>
  <section aria-label="expense period summary">
    <Card variant="compact" class="flex flex-col gap-3">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
        <h2 class="min-w-0 text-base font-semibold text-surface-light">
          Spent on
          <span v-if="monthLabel">{{ monthLabel }}</span>
          <span v-else class="text-surface-mid">…</span>
        </h2>
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

      <div class="flex flex-wrap items-end justify-between gap-3 border-t border-surface-border/50 pt-3">
        <div class="min-w-0">
          <p class="text-xs font-medium uppercase tracking-wide text-surface-mid">Total</p>
          <p
            v-if="summary"
            class="mt-1 truncate text-2xl font-bold font-data text-surface-light sm:text-3xl"
          >
            {{ formatMoney(summary.total, summary.currency) }}
          </p>
          <p
            v-else
            class="mt-1 animate-pulse text-2xl font-bold text-surface-border sm:text-3xl"
            aria-hidden="true"
          >
            —
          </p>
        </div>
        <ToolbarPillButton
          family="1xx"
          class="shrink-0"
          :aria-label="`open transactions, ${expenseTotal} items`"
          @click="emit('openTransactions')"
        >
          transactions · {{ expenseTotal }}
        </ToolbarPillButton>
      </div>

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
    </Card>
  </section>
</template>
