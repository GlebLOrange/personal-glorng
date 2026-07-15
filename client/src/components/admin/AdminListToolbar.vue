<script setup lang="ts">
import { computed, useSlots } from "vue";

import BasePagination from "@/components/ui/BasePagination.vue";

defineProps<{
  total: number;
  page: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  itemLabel?: string;
  ariaLabel: string;
  loading?: boolean;
}>();

const emit = defineEmits<{ prev: []; next: [] }>();

const slots = useSlots();
const hasStartSlot = computed(() => Boolean(slots.start));
</script>

<template>
  <div
    v-if="hasStartSlot"
    class="grid grid-cols-[1fr_auto_1fr] max-sm:grid-cols-1 max-sm:justify-items-center items-center gap-3 max-sm:gap-2"
  >
    <div class="justify-self-start min-w-0 max-sm:justify-self-center">
      <slot name="start" />
    </div>
    <p class="text-xs text-surface-muted text-center justify-self-center whitespace-nowrap">
      {{ total }} {{ itemLabel ?? "items" }} · page {{ page }} of {{ Math.max(totalPages, 1) }}
    </p>
    <div class="justify-self-end max-sm:justify-self-center">
      <BasePagination
        layout="compact"
        :ariaLabel="ariaLabel"
        :page="page"
        :has-next-page="hasNextPage"
        :has-previous-page="hasPreviousPage"
        :loading="loading"
        @prev="emit('prev')"
        @next="emit('next')"
      />
    </div>
  </div>
  <div v-else class="flex flex-wrap items-center justify-between gap-3">
    <p class="text-xs text-surface-muted">
      {{ total }} {{ itemLabel ?? "items" }} · page {{ page }} of {{ Math.max(totalPages, 1) }}
    </p>
    <BasePagination
      layout="compact"
      :ariaLabel="ariaLabel"
      :page="page"
      :has-next-page="hasNextPage"
      :has-previous-page="hasPreviousPage"
      :loading="loading"
      @prev="emit('prev')"
      @next="emit('next')"
    />
  </div>
</template>
