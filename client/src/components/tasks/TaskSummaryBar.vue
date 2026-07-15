<script setup lang="ts">
import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import { Card } from "@/components/ui/card";
import { statusBadgeClass, statusLabel } from "@/constants/taskStatus";
import type { TaskStats } from "@/types";

const CHIP_STATUSES = ["not_completed", "postponed", "cancelled"] as const;

defineProps<{
  stats: TaskStats | null;
  loading: boolean;
}>();

const filterStatus = defineModel<string>("filterStatus", { required: true });

const emit = defineEmits<{
  switchTab: [tab: string];
}>();

const skeletonCards = 4;

function setFilter(status: string): void {
  filterStatus.value = status;
}

function cardActiveClass(active: boolean): string {
  return active ? "ring-2 ring-accent-blue/50 border-accent-blue/40" : "";
}
</script>

<template>
  <div class="mb-6 space-y-3">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <template v-if="loading && !stats">
        <Card v-for="n in skeletonCards" :key="n" class="animate-pulse">
          <div class="h-7 w-12 bg-surface-border rounded mb-2" />
          <div class="h-3 w-16 bg-surface-border rounded" />
        </Card>
      </template>

      <template v-else-if="stats">
        <Card
          as="button"
          type="button"
          interactive
          hoverable
          :class="cardActiveClass(!filterStatus)"
          :aria-pressed="!filterStatus"
          aria-label="Show all tasks"
          @click="setFilter('')"
        >
          <div class="text-2xl font-bold text-surface-light">{{ stats.total }}</div>
          <div class="text-xs text-surface-mid mt-1">Total</div>
        </Card>
        <Card
          as="button"
          type="button"
          interactive
          hoverable
          :class="cardActiveClass(filterStatus === 'pending')"
          :aria-pressed="filterStatus === 'pending'"
          aria-label="Filter pending tasks"
          @click="setFilter('pending')"
        >
          <div class="text-2xl font-bold text-status-warning">{{ stats.pending }}</div>
          <div class="text-xs text-surface-mid mt-1">Pending</div>
        </Card>
        <Card
          as="button"
          type="button"
          interactive
          hoverable
          :class="cardActiveClass(filterStatus === 'completed')"
          :aria-pressed="filterStatus === 'completed'"
          aria-label="Filter completed tasks"
          @click="setFilter('completed')"
        >
          <div class="text-2xl font-bold text-status-success">{{ stats.completed }}</div>
          <div class="text-xs text-surface-mid mt-1">Completed</div>
        </Card>
        <Card
          as="button"
          type="button"
          interactive
          hoverable
          :class="[
            stats.failed_syncs > 0 ? 'border-status-error/40' : '',
            cardActiveClass(false),
          ]"
          aria-label="View failed syncs"
          @click="emit('switchTab', 'sync')"
        >
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

    <div class="flex flex-wrap items-center gap-2 justify-between">
      <div class="flex flex-wrap items-center gap-2">
        <AdminFilterChip
          label="All"
          :active="!filterStatus"
          color-class="text-surface-light bg-surface-dark"
          @click="setFilter('')"
        />
        <AdminFilterChip
          v-for="status in CHIP_STATUSES"
          :key="status"
          :label="statusLabel(status)"
          :active="filterStatus === status"
          :color-class="statusBadgeClass(status)"
          @click="setFilter(status)"
        />
      </div>
      <slot name="actions" />
    </div>
  </div>
</template>
