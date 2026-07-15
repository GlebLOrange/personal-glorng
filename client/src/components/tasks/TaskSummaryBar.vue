<script setup lang="ts">
import { Card } from "@/components/ui/card";
import type { TaskStats } from "@/types";

defineProps<{
  stats: TaskStats | null;
  loading: boolean;
}>();

const skeletonCards = 4;
</script>

<template>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
    <template v-if="loading && !stats">
      <Card v-for="n in skeletonCards" :key="n" class="animate-pulse">
        <div class="h-7 w-12 bg-surface-border rounded mb-2" />
        <div class="h-3 w-16 bg-surface-border rounded" />
      </Card>
    </template>

    <template v-else-if="stats">
      <Card>
        <div class="text-2xl font-bold text-surface-light">{{ stats.total }}</div>
        <div class="text-xs text-surface-mid mt-1">Total</div>
      </Card>
      <Card>
        <div class="text-2xl font-bold text-status-warning">{{ stats.pending }}</div>
        <div class="text-xs text-surface-mid mt-1">Pending</div>
      </Card>
      <Card>
        <div class="text-2xl font-bold text-status-success">{{ stats.completed }}</div>
        <div class="text-xs text-surface-mid mt-1">Completed</div>
      </Card>
      <Card :class="stats.failed_syncs > 0 ? 'border-status-error/40' : ''">
        <div
          :class="[
            'text-2xl font-bold',
            stats.failed_syncs > 0 ? 'text-status-error' : 'text-surface-light',
          ]"
        >
          {{ stats.failed_syncs }}
        </div>
        <div class="text-xs text-surface-mid mt-1">Failed syncs</div>
      </Card>
    </template>
  </div>
</template>
