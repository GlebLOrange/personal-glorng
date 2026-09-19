<script setup lang="ts">
import { computed } from "vue";

import { Card } from "@/components/ui/card";
import type { ExpenseSummary } from "@/types";

const props = defineProps<{
  summary: ExpenseSummary | null;
  expenseTotal: number;
  formatMoney: (amount: string | number, currency: string) => string;
}>();

const topCategory = computed(() => {
  const items = props.summary?.by_category;
  if (!items?.length) return null;
  let best = items[0]!;
  let bestValue = parseFloat(String(best.total));
  for (const item of items.slice(1)) {
    const value = parseFloat(String(item.total));
    if (value > bestValue) {
      best = item;
      bestValue = value;
    }
  }
  return best.category;
});
</script>

<template>
  <div class="grid grid-cols-1 gap-3 sm:grid-cols-3 sm:gap-4">
    <Card variant="compact" class="min-w-0">
      <p class="text-xs uppercase tracking-wide text-surface-mid">Total Expenses</p>
      <p
        v-if="summary"
        class="mt-1 truncate text-xl font-bold font-data text-surface-light sm:text-2xl"
      >
        {{ formatMoney(summary.total, summary.currency) }}
      </p>
      <p v-else class="mt-1 animate-pulse text-xl font-bold text-surface-border sm:text-2xl">—</p>
    </Card>

    <Card variant="compact" class="min-w-0">
      <p class="text-xs uppercase tracking-wide text-surface-mid">Transactions</p>
      <p class="mt-1 text-xl font-bold font-data text-surface-light sm:text-2xl">
        {{ expenseTotal }}
      </p>
    </Card>

    <Card variant="compact" class="min-w-0">
      <p class="text-xs uppercase tracking-wide text-surface-mid">Top Category</p>
      <p
        v-if="topCategory"
        class="mt-1 truncate text-xl font-bold text-surface-light sm:text-2xl"
      >
        {{ topCategory }}
      </p>
      <p v-else class="mt-1 text-xl font-bold font-data text-surface-border sm:text-2xl">—</p>
    </Card>
  </div>
</template>
