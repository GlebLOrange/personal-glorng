<script setup lang="ts">
import { computed } from "vue";

import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { Card } from "@/components/ui/card";
import type { Expense, ExpenseSummary } from "@/types";

const props = defineProps<{
  monthLabel: string;
  summary: ExpenseSummary | null;
  expenseTotal: number;
  summaryError: string | null;
  ratesError: string | null;
  recentExpenses: Expense[];
  formatMoney: (amount: string | number, currency: string) => string;
  formatExpenseDate: (iso: string) => string;
}>();

const emit = defineEmits<{
  retry: [];
  openActivity: [];
}>();

/** Metric amount + smaller currency unit (Toss: number dominant, unit legible). */
const totalParts = computed((): { amount: string; unit: string | null } | null => {
  if (!props.summary) return null;
  const num =
    typeof props.summary.total === "string"
      ? parseFloat(props.summary.total)
      : Number(props.summary.total);
  if (!Number.isFinite(num)) return { amount: "N/A", unit: null };
  const parts = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: props.summary.currency,
    minimumFractionDigits: 2,
  }).formatToParts(num);
  const unit =
    parts
      .filter((part) => part.type === "currency")
      .map((part) => part.value)
      .join("") || null;
  const amount = parts
    .filter((part) => part.type !== "currency")
    .map((part) => part.value)
    .join("")
    .trim();
  return { amount, unit };
});
</script>

<template>
  <section aria-label="expense period summary">
    <Card variant="compact" class="flex flex-col gap-3">
      <h2 class="min-w-0 text-base font-semibold text-surface-light">
        Spent on
        <span v-if="monthLabel">{{ monthLabel }}</span>
        <span v-else class="text-surface-mid">…</span>
      </h2>

      <div
        class="flex flex-wrap items-start justify-between gap-3 border-t border-surface-border/50 pt-3"
      >
        <div class="min-w-0">
          <p class="text-label text-surface-mid">total</p>
          <p v-if="totalParts" class="mt-1 truncate text-metric">
            <span>{{ totalParts.amount }}</span>
            <span v-if="totalParts.unit" class="ml-1 text-sm font-medium text-surface-mid">{{
              ` ${totalParts.unit}`
            }}</span>
          </p>
          <p v-else class="mt-1 animate-pulse text-metric text-surface-border" aria-hidden="true">
            —
          </p>
        </div>

        <div class="ml-auto flex w-full max-w-xs flex-col items-stretch gap-1.5 sm:w-[15rem]">
          <ul
            v-if="recentExpenses.length"
            class="flex w-full flex-col gap-1"
            aria-label="recent expenses"
          >
            <li
              v-for="expense in recentExpenses"
              :key="expense.id"
              class="flex items-baseline justify-between gap-2 text-xs"
            >
              <span class="min-w-0 truncate text-surface-light">
                {{ expense.tool_name }}
                <span class="text-[10px] text-surface-mid">
                  · {{ formatExpenseDate(expense.expense_date) }}
                </span>
              </span>
              <span class="shrink-0 font-data text-surface-mid">
                {{ formatMoney(expense.amount, expense.currency) }}
              </span>
            </li>
          </ul>
          <p v-else class="text-xs text-surface-mid">No expenses this month yet.</p>
          <ToolbarPillButton
            action="create"
            class="mt-auto w-full shrink-0"
            :aria-label="`open recent activity, ${expenseTotal} items`"
            @click="emit('openActivity')"
          >
            recent activity
          </ToolbarPillButton>
        </div>
      </div>

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
