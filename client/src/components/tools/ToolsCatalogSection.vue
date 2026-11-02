<script setup lang="ts">
import { FOCUS_RING_DEFAULT } from "@/constants/httpStatusColors";

defineProps<{
  id: string;
  label: string;
  count: number;
  /** Controlled open state (mobile collapsed / one-open accordion). */
  open: boolean;
}>();

const emit = defineEmits<{
  toggle: [open: boolean];
}>();

const SUMMARY_CLASS = `flex min-h-11 cursor-pointer list-none items-center gap-2 rounded-lg px-3 py-2 outline-none transition-colors motion-reduce:transition-none hover:bg-surface-grid/50 focus-visible:ring-2 ${FOCUS_RING_DEFAULT} [&::-webkit-details-marker]:hidden`;

const DETAILS_CLASS =
  "group scroll-mt-[calc(var(--page-chrome-h,var(--page-chrome-h-fallback))+4.25rem)] rounded-xl border border-transparent bg-surface-card/40 open:bg-surface-card/55";

function countLabel(count: number): string {
  return count === 1 ? "1 tool" : `${count} tools`;
}

function onToggle(event: Event): void {
  const el = event.target as HTMLDetailsElement;
  emit("toggle", el.open);
}
</script>

<template>
  <details :id="id" :open="open" :class="DETAILS_CLASS" @toggle="onToggle">
    <summary :class="SUMMARY_CLASS">
      <span
        class="inline-block text-surface-mid transition-transform duration-200 motion-reduce:transition-none group-open:rotate-90"
        aria-hidden="true"
        >▸</span
      >
      <h2 class="text-sm font-semibold text-surface-light">
        <span aria-hidden="true">{{ label }}</span>
        <span class="sr-only">{{ label }}, {{ countLabel(count) }}</span>
      </h2>
      <span class="ml-auto text-xs font-medium text-text-muted" aria-hidden="true">{{ count }}</span>
    </summary>
    <div class="border-t border-surface-border/70 px-3 pb-3 pt-3">
      <slot />
    </div>
  </details>
</template>
