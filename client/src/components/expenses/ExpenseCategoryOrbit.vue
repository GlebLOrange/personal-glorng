<script setup lang="ts">
import { computed } from "vue";

import { Card } from "@/components/ui/card";
import type { ExpenseSummary } from "@/types";

type OrbitSize = "sm" | "md" | "lg";

type OrbitRow = {
  category: string;
  total: number;
  percent: number;
  size: OrbitSize;
};

const props = defineProps<{
  summary: ExpenseSummary | null;
  formatMoney: (amount: string | number, currency: string) => string;
  /** When true, wrap in a Card with a heading (breakdown panel). */
  framed?: boolean;
}>();

const emit = defineEmits<{
  selectCategory: [category: string];
}>();

const currency = computed(() => props.summary?.currency ?? "PLN");

function sizeForPercent(percent: number): OrbitSize {
  if (percent >= 35) return "lg";
  if (percent >= 15) return "md";
  return "sm";
}

const rows = computed((): OrbitRow[] => {
  if (!props.summary?.by_category.length) return [];
  const total = parseFloat(String(props.summary.total));
  return [...props.summary.by_category]
    .map((item) => {
      const value = parseFloat(String(item.total));
      const percent = total > 0 ? Math.round((value / total) * 100) : 0;
      return {
        category: item.category,
        total: value,
        percent,
        size: sizeForPercent(percent),
      };
    })
    .sort((a, b) => b.total - a.total);
});

function discClass(size: OrbitSize): string {
  // All sizes ≥ 44px hit target; lg/md grow for spend hierarchy.
  const sizeClass =
    size === "lg" ? "size-14 text-base" : size === "md" ? "size-12 text-sm" : "size-11 text-xs";
  return `flex ${sizeClass} shrink-0 cursor-pointer items-center justify-center rounded-full border border-transparent bg-surface-dark font-semibold text-surface-light transition-[transform,background-color,border-color] duration-200 motion-reduce:transition-none hover:border-accent-blue/40 hover:bg-accent-blue/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50`;
}

function planetInitial(category: string): string {
  const trimmed = category.trim();
  return trimmed ? trimmed[0]!.toUpperCase() : "?";
}

function onSelect(category: string): void {
  emit("selectCategory", category);
}
</script>

<template>
  <component :is="framed ? Card : 'div'" :class="framed ? undefined : 'min-w-0'">
    <h3
      v-if="framed"
      class="mb-3 text-sm font-semibold text-surface-light"
    >
      spend by category
    </h3>
    <ul
      v-if="rows.length"
      class="flex flex-wrap items-end justify-center gap-x-4 gap-y-3 md:justify-start"
      aria-label="spend by category"
    >
      <li
        v-for="row in rows"
        :key="row.category"
        class="flex max-w-[6.5rem] flex-col items-center gap-1.5"
      >
        <button
          type="button"
          :class="discClass(row.size)"
          :aria-label="`${row.category}, ${formatMoney(row.total, currency)}, ${row.percent}%`"
          @click="onSelect(row.category)"
        >
          <span aria-hidden="true">{{ planetInitial(row.category) }}</span>
        </button>
        <span class="w-full truncate text-center text-xs text-surface-light">{{ row.category }}</span>
        <span class="font-data text-center text-[11px] text-surface-mid">
          {{ formatMoney(row.total, currency) }}
          <span class="ml-0.5">{{ row.percent }}%</span>
        </span>
      </li>
    </ul>
    <!-- Framed (breakdown): show empty copy. Dashboard: stay quiet when no summary yet. -->
    <p v-else-if="framed" class="text-sm text-surface-mid">No data available yet.</p>
  </component>
</template>
