<script setup lang="ts">
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import { batchLabel } from "@/composables/useDataExtractTool";
import type { ImportBatchSummary, ImportResult, PromoteBatchResult } from "@/types/dataExtract";

defineProps<{
  batchHistory: ImportBatchSummary[];
  batchTotal: number;
  batchPage: number;
  batchTotalPages: number;
  hasNextBatchPage: boolean;
  hasPreviousBatchPage: boolean;
  selectedBatchId: number | null;
  importResult: ImportResult | null;
  importSummary: string;
  selectedBatch: ImportBatchSummary | null;
  canPromoteSelected: boolean;
  promoteResult: PromoteBatchResult | null;
  loading: boolean;
}>();

const emit = defineEmits<{
  refresh: [];
  select: [batchId: number];
  promote: [];
  first: [];
  prev: [];
  next: [];
  last: [];
}>();
</script>

<template>
  <div class="space-y-6">
    <Card v-if="batchHistory.length" class="mb-6 space-y-3">
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-lg font-semibold text-surface-light">Recent imports</h2>
        <BaseButton variant="ghost" @click="emit('refresh')">refresh</BaseButton>
      </div>
      <ul class="space-y-2">
        <li v-for="batch in batchHistory" :key="batch.id">
          <button
            type="button"
            :class="[
              'w-full rounded-md border px-3 py-2 text-left text-sm transition-colors',
              selectedBatchId === batch.id
                ? 'border-accent-blue bg-accent-blue/10 text-surface-light'
                : 'border-surface-border text-surface-mid hover:border-accent-blue',
            ]"
            @click="emit('select', batch.id)"
          >
            {{ batchLabel(batch) }}
          </button>
        </li>
      </ul>
      <AdminListFooter
        v-if="batchHistory.length > 0"
        :total="batchTotal"
        :page="batchPage"
        :total-pages="batchTotalPages"
        :has-next-page="hasNextBatchPage"
        :has-previous-page="hasPreviousBatchPage"
        item-label="batches"
        ariaLabel="Import batches pagination"
        @first="emit('first')"
        @prev="emit('prev')"
        @next="emit('next')"
        @last="emit('last')"
      />
    </Card>

    <Card v-if="importResult" class="mb-6 space-y-3">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-lg font-semibold text-surface-light">Import batch</h2>
          <p class="text-sm text-surface-mid">{{ importSummary }}</p>
          <p v-if="importResult.error_count > 0" class="font-data text-xs text-status-cyan">
            {{ importResult.error_count }} row(s) failed parsing and were stored with errors.
          </p>
          <p v-if="selectedBatch?.promoted_count" class="mt-1 text-xs text-status-success">
            {{ selectedBatch.promoted_count }} row(s) promoted to embed storage.
          </p>
        </div>
        <BaseButton
          v-if="canPromoteSelected"
          variant="secondary"
          :disabled="loading"
          @click="emit('promote')"
        >
          {{ loading ? "working..." : "promote pipe embed rows" }}
        </BaseButton>
      </div>
      <p v-if="promoteResult" class="text-xs text-surface-mid">
        Promoted {{ promoteResult.promoted }}, skipped {{ promoteResult.skipped }}
        <span v-if="promoteResult.errors.length">, {{ promoteResult.errors.length }} error(s)</span
        >.
      </p>
    </Card>
  </div>
</template>
