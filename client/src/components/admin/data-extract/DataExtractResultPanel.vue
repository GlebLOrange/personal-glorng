<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import IconCopyButton from "@/components/ui/IconCopyButton.vue";
import { Card } from "@/components/ui/card";
import { formatDataExtractCell } from "@/composables/useDataExtractTool";
import type { ExtractionResult, ImportResult } from "@/types/dataExtract";

const showRawJson = defineModel<boolean>("showRawJson", { required: true });

defineProps<{
  result: ExtractionResult;
  importResult: ImportResult | null;
  metaSummary: string;
  tableColumns: string[];
  tableRows: Record<string, unknown>[];
  resultJson: string;
}>();

const emit = defineEmits<{
  copy: [];
  download: [];
}>();
</script>

<template>
  <Card class="space-y-4">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-lg font-semibold text-surface-light">Results</h2>
        <p class="mt-1 text-xs text-surface-mid">{{ metaSummary }}</p>
      </div>
      <div class="flex gap-2">
        <IconCopyButton aria-label="copy json" @click="emit('copy')" />
        <BaseButton variant="ghost" @click="emit('download')">download json</BaseButton>
        <BaseButton variant="ghost" @click="showRawJson = !showRawJson">
          {{ showRawJson ? "hide raw json" : "show raw json" }}
        </BaseButton>
      </div>
    </div>

    <div v-if="tableRows.length && tableColumns.length" class="overflow-x-auto">
      <table class="min-w-full text-left text-sm">
        <thead>
          <tr class="border-b border-surface-border text-surface-mid">
            <th v-for="column in tableColumns" :key="column" class="px-3 py-2 font-medium">
              {{ column }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, index) in tableRows.slice(0, 50)"
            :key="index"
            class="border-b border-surface-border/60"
          >
            <td v-for="column in tableColumns" :key="column" class="px-3 py-2 text-surface-light">
              {{ formatDataExtractCell(row[column]) }}
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="tableRows.length > 50" class="mt-2 text-xs text-surface-mid">
        Showing first 50 of {{ tableRows.length }} rows.
      </p>
    </div>

    <div v-if="importResult?.errors.length" class="alert-surface-warning space-y-2 p-4">
      <h3 class="text-sm font-medium">Parse errors</h3>
      <ul class="space-y-1 text-xs text-surface-mid">
        <li v-for="(error, index) in importResult.errors.slice(0, 10)" :key="index">
          Line {{ error.line_number ?? "?" }}: {{ error.message }}
        </li>
      </ul>
    </div>

    <pre
      v-if="showRawJson"
      class="overflow-x-auto rounded-md border border-surface-border bg-surface-dark p-4 text-xs text-surface-light"
      >{{ resultJson }}</pre>
  </Card>
</template>
