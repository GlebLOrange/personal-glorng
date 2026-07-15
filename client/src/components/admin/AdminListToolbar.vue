<script setup lang="ts">
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
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-3">
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
