<script setup lang="ts">
import { computed } from "vue";

import BaseCard from "@/components/ui/BaseCard.vue";
import type { ToolExpenseSummary } from "@/types";

const props = defineProps<{
  summary: ToolExpenseSummary | null;
  monthLabel: string;
  formatMoney: (amount: string | number, currency: string) => string;
}>();

const categoryBreakdown = computed(() => {
  if (!props.summary || props.summary.by_category.length === 0) return [];
  const total = parseFloat(String(props.summary.total));
  if (total <= 0) return [];

  return props.summary.by_category.map((item) => {
    const value = parseFloat(String(item.total));
    return {
      category: item.category,
      total: item.total,
      percent: Math.round((value / total) * 100),
    };
  });
});
</script>

<template>
  <BaseCard class="flex flex-col gap-4">
    <div>
      <p class="text-xs text-surface-mid font-mono uppercase tracking-wider">
        Total for {{ monthLabel }}
      </p>
      <p v-if="summary" class="text-2xl font-bold text-surface-light">
        {{ formatMoney(summary.total, summary.currency) }}
      </p>
      <p v-else class="text-2xl font-bold text-surface-border animate-pulse">—</p>
    </div>

    <div v-if="categoryBreakdown.length > 0" class="flex flex-col gap-2 border-t border-surface-border pt-3">
      <p class="text-[10px] text-surface-mid font-mono uppercase tracking-wider">By category</p>
      <div
        v-for="item in categoryBreakdown"
        :key="item.category"
        class="flex flex-col gap-1"
      >
        <div class="flex justify-between text-xs font-mono">
          <span class="text-surface-light">{{ item.category }}</span>
          <span class="text-surface-mid">
            {{ formatMoney(item.total, summary!.currency) }}
            <span class="text-surface-mid/70">· {{ item.percent }}%</span>
          </span>
        </div>
        <div class="h-1.5 bg-surface-border rounded-full overflow-hidden">
          <div
            class="h-full bg-accent-blue rounded-full transition-all"
            :style="{ width: `${item.percent}%` }"
          />
        </div>
      </div>
    </div>
  </BaseCard>
</template>
