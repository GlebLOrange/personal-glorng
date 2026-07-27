<script setup lang="ts">
import { computed } from "vue";

import IconActionButton from "@/components/ui/IconActionButton.vue";

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

const emit = defineEmits<{ prev: []; next: []; first: []; last: [] }>();

const showPagination = computed(() => props.totalPages > 1);

const totalLabel = computed(() => {
  if (props.countLabel) return props.countLabel;
  const label = props.itemLabel ?? "items";
  if (props.visibleCount !== undefined) {
    return `showing ${props.visibleCount} of ${props.total} ${label}`;
  }
  return `${props.total} ${label}`;
});

const pageLabel = computed(() => `page ${props.page} of ${props.totalPages}`);

const prevDisabled = computed(() => props.loading || !props.hasPreviousPage);
const nextDisabled = computed(() => props.loading || !props.hasNextPage);
</script>

<template>
  <nav
    v-if="showPagination"
    class="mt-4 grid grid-cols-[auto_1fr_auto] items-center gap-3"
    :aria-label="ariaLabel"
  >
    <div class="flex flex-wrap items-center gap-1">
      <IconActionButton
        family="1xx"
        :disabled="prevDisabled"
        title="to start"
        aria-label="to start"
        @click="emit('first')"
      >
        &lt;&lt;
      </IconActionButton>
      <IconActionButton
        family="1xx"
        :disabled="prevDisabled"
        title="previous"
        aria-label="previous"
        @click="emit('prev')"
      >
        &lt;
      </IconActionButton>
    </div>
    <p
      class="flex flex-wrap items-center justify-center gap-x-2.5 text-center text-label tracking-wide"
    >
      <span class="font-data text-surface-light">{{ totalLabel }}</span>
      <span class="text-surface-border" aria-hidden="true">·</span>
      <span class="font-data text-surface-light">{{ pageLabel }}</span>
    </p>
    <div class="flex flex-wrap items-center justify-end gap-1">
      <IconActionButton
        family="1xx"
        :disabled="nextDisabled"
        title="next"
        aria-label="next"
        @click="emit('next')"
      >
        &gt;
      </IconActionButton>
      <IconActionButton
        family="1xx"
        :disabled="nextDisabled"
        title="to end"
        aria-label="to end"
        @click="emit('last')"
      >
        &gt;&gt;
      </IconActionButton>
    </div>
  </nav>
</template>
