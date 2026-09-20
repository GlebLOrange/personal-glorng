<script setup lang="ts">
import { Card } from "@/components/ui/card";
import type { ExpenseSummary } from "@/types";

defineProps<{
  summary: ExpenseSummary | null;
  expenseTotal: number;
  formatMoney: (amount: string | number, currency: string) => string;
}>();

defineEmits<{
  openTransactions: [];
}>();
</script>

<template>
  <Card variant="compact" class="min-w-0">
    <div class="flex flex-wrap items-end justify-between gap-2">
      <div class="min-w-0">
        <p class="text-xs uppercase tracking-wide text-surface-mid">Total</p>
        <p
          v-if="summary"
          class="mt-1 truncate text-2xl font-bold font-data text-surface-light sm:text-3xl"
        >
          {{ formatMoney(summary.total, summary.currency) }}
        </p>
        <p v-else class="mt-1 animate-pulse text-2xl font-bold text-surface-border sm:text-3xl">
          —
        </p>
      </div>
      <button
        type="button"
        class="text-sm text-accent-blue underline-offset-2 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
        @click="$emit('openTransactions')"
      >
        transactions · {{ expenseTotal }}
      </button>
    </div>
  </Card>
</template>
