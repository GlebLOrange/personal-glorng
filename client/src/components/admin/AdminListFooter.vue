<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";

const props = defineProps<{
  total: number;
  page: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  itemLabel?: string;
  ariaLabel: string;
  loading?: boolean;
  visibleCount?: number;
  countLabel?: string;
}>();

const emit = defineEmits<{ prev: []; next: [] }>();

const totalLabel = computed(() => {
  if (props.countLabel) return props.countLabel;
  const label = props.itemLabel ?? "items";
  if (props.visibleCount !== undefined) {
    return `showing ${props.visibleCount} of ${props.total} ${label}`;
  }
  return `${props.total} ${label}`;
});

const pageLabel = computed(
  () => `page ${props.page} of ${Math.max(props.totalPages, 1)}`,
);

const prevDisabled = computed(() => props.loading || !props.hasPreviousPage);
const nextDisabled = computed(() => props.loading || !props.hasNextPage);
</script>

<template>
  <nav
    class="mt-4 grid grid-cols-[auto_1fr_auto] items-center gap-3"
    :aria-label="ariaLabel"
  >
    <BaseButton variant="ghost" :disabled="prevDisabled" @click="emit('prev')">
      previous
    </BaseButton>
    <p class="flex flex-wrap items-center justify-center gap-x-2 text-center text-xs text-surface-muted">
      <span>{{ totalLabel }}</span>
      <span aria-hidden="true">·</span>
      <span>{{ pageLabel }}</span>
    </p>
    <BaseButton variant="ghost" :disabled="nextDisabled" @click="emit('next')">
      next
    </BaseButton>
  </nav>
</template>
