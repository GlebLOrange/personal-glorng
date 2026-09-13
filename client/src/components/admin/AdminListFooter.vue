<script setup lang="ts">
import { computed, useSlots } from "vue";

import IconActionButton from "@/components/ui/IconActionButton.vue";

const props = withDefaults(
  defineProps<{
    total: number;
    page: number;
    totalPages: number;
    hasNextPage: boolean;
    hasPreviousPage: boolean;
    itemLabel?: string;
    ariaLabel?: string;
    loading?: boolean;
    visibleCount?: number;
    countLabel?: string;
    /** When set, controls the meta/leading slot (avoids conditional-slot detection). */
    showLeading?: boolean;
  }>(),
  {
    ariaLabel: "pagination",
  },
);

const emit = defineEmits<{ prev: []; next: []; first: []; last: [] }>();
const slots = useSlots();

const showPagination = computed(() => props.totalPages > 1);
const hasLeading = computed(() =>
  props.showLeading !== undefined ? props.showLeading : Boolean(slots.leading),
);
const showBar = computed(() => showPagination.value || hasLeading.value);

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

const navClass = computed(() => {
  if (showPagination.value) {
    return "mt-4 grid grid-cols-[auto_1fr_auto] items-center gap-3";
  }
  return "mt-4 flex flex-wrap items-center justify-center gap-3";
});
</script>

<template>
  <nav v-if="showBar" :class="navClass" :aria-label="ariaLabel">
    <template v-if="showPagination">
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
      <div
        class="flex min-w-0 flex-wrap items-center justify-center gap-x-2.5 text-center text-label tracking-wide"
      >
        <div v-if="hasLeading" class="min-w-0">
          <slot name="leading" />
        </div>
        <template v-if="hasLeading">
          <span class="text-surface-border" aria-hidden="true">·</span>
        </template>
        <template v-else>
          <span class="font-data text-surface-light">{{ totalLabel }}</span>
          <span class="text-surface-border" aria-hidden="true">·</span>
        </template>
        <span class="font-data text-surface-light">{{ pageLabel }}</span>
      </div>
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
    </template>
    <div v-else-if="hasLeading" class="min-w-0">
      <slot name="leading" />
    </div>
  </nav>
</template>
