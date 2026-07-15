<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";

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
    return `Page ${props.page} of ${props.totalPages}`;
  }
  return `Page ${props.page}`;
});

const prevDisabled = computed(() => props.loading || !canGoPrevious.value);
const nextDisabled = computed(() => props.loading || !props.hasNextPage);
</script>

<template>
  <nav
    :aria-label="ariaLabel"
    :class="
      layout === 'compact' ? 'flex items-center gap-2' : 'flex items-center justify-between'
    "
  >
    <BaseButton variant="ghost" size="sm" :disabled="prevDisabled" @click="emit('prev')">
      Previous
    </BaseButton>
    <span v-if="layout === 'bar'" class="text-xs text-surface-muted">{{ pageLabel }}</span>
    <BaseButton variant="ghost" size="sm" :disabled="nextDisabled" @click="emit('next')">
      Next
    </BaseButton>
  </nav>
</template>
