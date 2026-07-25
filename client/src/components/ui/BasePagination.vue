<script setup lang="ts">
import { computed } from "vue";

import IconActionButton from "@/components/ui/IconActionButton.vue";

const props = withDefaults(
  defineProps<{
    page: number;
    hasNextPage: boolean;
    hasPreviousPage?: boolean;
    totalPages?: number;
    ariaLabel: string;
    loading?: boolean;
    layout?: "bar" | "compact";
  }>(),
  {
    loading: false,
    layout: "bar",
    hasPreviousPage: undefined,
    totalPages: undefined,
  },
);

const emit = defineEmits<{ prev: []; next: [] }>();

const canGoPrevious = computed(() => {
  if (props.hasPreviousPage !== undefined) return props.hasPreviousPage;
  return props.page > 1;
});

const pageLabel = computed(() => {
  if (props.totalPages !== undefined && props.totalPages > 0) {
    return `page ${props.page} of ${props.totalPages}`;
  }
  return `page ${props.page}`;
});

const prevDisabled = computed(() => props.loading || !canGoPrevious.value);
const nextDisabled = computed(() => props.loading || !props.hasNextPage);
</script>

<template>
  <nav
    :aria-label="ariaLabel"
    :class="layout === 'compact' ? 'flex items-center gap-2' : 'flex items-center justify-between'"
  >
    <IconActionButton
      family="1xx"
      :disabled="prevDisabled"
      aria-label="previous"
      title="previous"
      @click="emit('prev')"
    >
      &lt;
    </IconActionButton>
    <span v-if="layout === 'bar'" class="text-xs text-surface-muted">{{ pageLabel }}</span>
    <IconActionButton
      family="1xx"
      :disabled="nextDisabled"
      aria-label="next"
      title="next"
      @click="emit('next')"
    >
      &gt;
    </IconActionButton>
  </nav>
</template>
