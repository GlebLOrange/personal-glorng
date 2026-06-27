<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import { usePermissions } from "@/composables/usePermissions";
import { SELECT_CLASS } from "@/constants/formClasses";
import type {
  DataExtractFormat,
  DelimitedProfile,
  ExtractionResult,
  ImportBatchDetail,
  ImportBatchSummary,
  ImportResult,
  PromoteBatchResult,
  XmlExtractMode,
} from "@/types/dataExtract";

type FormatChoice = "auto" | DataExtractFormat;

const selectedFile = ref<File | null>(null);
const dragOver = ref(false);
const formatChoice = ref<FormatChoice>("auto");
const profileChoice = ref<DelimitedProfile>("custom");
const fieldDelimiter = ref("|");
const listDelimiter = ref(";");
const rowTag = ref("");
const xmlMode = ref<XmlExtractMode>("rows");
const showRawJson = ref(false);
const result = ref<ExtractionResult | null>(null);
const importResult = ref<ImportResult | null>(null);
const batchHistory = ref<ImportBatchSummary[]>([]);
const selectedBatchId = ref<number | null>(null);
const batchDetail = ref<ImportBatchDetail | null>(null);
const promoteResult = ref<PromoteBatchResult | null>(null);

const fileInputRef = ref<HTMLInputElement | null>(null);
const { loading, run } = useApiAction();
const { copy } = useClipboard();
const { can } = usePermissions();

const canWrite = computed(() => can("data-extract", "write"));
const selectedName = computed(() => selectedFile.value?.name ?? "");
const selectedBatch = computed(
  () =>
    batchDetail.value?.batch ??
    batchHistory.value.find((b) => b.id === selectedBatchId.value) ??
    null,
);
const canPromoteSelected = computed(
  () =>
    canWrite.value &&
    selectedBatch.value?.profile === "pipe_embed" &&
    (selectedBatch.value?.row_count ?? 0) > 0,
);
const showXmlOptions = computed(
  () => formatChoice.value === "auto" || formatChoice.value === "xml",
);
const showDelimitedOptions = computed(
  () =>
    formatChoice.value === "delimited" ||
    profileChoice.value === "pipe_embed" ||
    formatChoice.value === "auto",
);

const metaSummary = computed(() => {
  if (!result.value) return "";
  const meta = result.value.meta;
  const parts = [
    `format: ${result.value.format}`,
    `rows: ${String(meta.row_count ?? result.value.records.length)}`,
  ];
  const columns = meta.columns;
  if (Array.isArray(columns) && columns.length) {
    parts.push(`columns: ${columns.length}`);
  }
  const errorCount = meta.error_count;
  if (typeof errorCount === "number" && errorCount > 0) {
    parts.push(`errors: ${errorCount}`);
  }
  if (typeof meta.filename === "string") {
    parts.push(String(meta.filename));
  }
  return parts.join(" · ");
});

const importSummary = computed(() => {
  if (!importResult.value) return "";
  const parts = [
    `batch #${importResult.value.batch_id}`,
    `imported: ${importResult.value.row_count}`,
  ];
  if (importResult.value.error_count > 0) {
    parts.push(`errors: ${importResult.value.error_count}`);
  }
  if (importResult.value.profile) {
    parts.push(`profile: ${importResult.value.profile}`);
  }
  return parts.join(" · ");
});

const tableColumns = computed((): string[] => {
  if (result.value) {
    const metaColumns = result.value.meta.columns;
    if (Array.isArray(metaColumns) && metaColumns.every((c) => typeof c === "string")) {
      return metaColumns as string[];
    }
    const first = result.value.records[0];
    if (first && typeof first === "object" && !Array.isArray(first)) {
      return Object.keys(first as Record<string, unknown>);
    }
    return [];
  }
  const first = importResult.value?.preview[0];
  if (first && typeof first === "object" && !Array.isArray(first)) {
    return Object.keys(first);
  }
  return [];
});

const tableRows = computed((): Record<string, unknown>[] => {
  const rows = result.value?.records ?? importResult.value?.preview ?? [];
  if (!tableColumns.value.length) return [];
  return rows.filter(
    (row): row is Record<string, unknown> =>
      typeof row === "object" && row !== null && !Array.isArray(row),
  );
});

const resultJson = computed(() => (showRawJson.value && result.value ? serializeResult() : ""));

function resetOutputs(): void {
  result.value = null;
  importResult.value = null;
  promoteResult.value = null;
}

function batchLabel(batch: ImportBatchSummary): string {
  const parts = [`#${batch.id}`, batch.filename, `${batch.row_count} rows`, batch.status];
  if (batch.promoted_count > 0) {
    parts.push(`${batch.promoted_count} promoted`);
  }
  return parts.join(" · ");
}

async function loadBatchHistory(): Promise<void> {
  const response = await api.get<{ items: ImportBatchSummary[] }>("/tools/data-extract/batches");
  batchHistory.value = response.data.items;
}

async function loadBatchDetail(batchId: number): Promise<void> {
  selectedBatchId.value = batchId;
  promoteResult.value = null;
  const response = await run(
    () => api.get<ImportBatchDetail>(`/tools/data-extract/batches/${batchId}`),
    { errorFallback: "Failed to load import batch" },
  );
  if (response) {
    batchDetail.value = response.data;
    result.value = {
      format: response.data.batch.format as DataExtractFormat,
      records: response.data.preview_rows.filter((row) => !row.error).map((row) => row.fields),
      meta: {
        row_count: response.data.batch.row_count,
        error_count: response.data.batch.error_count,
        profile: response.data.batch.profile,
      },
    };
    importResult.value = {
      batch_id: response.data.batch.id,
      format: response.data.batch.format,
      profile: response.data.batch.profile,
      row_count: response.data.batch.row_count,
      error_count: response.data.batch.error_count,
      preview: response.data.preview_rows.filter((row) => !row.error).map((row) => row.fields),
      errors: [],
    };
    showRawJson.value = false;
  }
}

async function promoteSelectedBatch(): Promise<void> {
  if (!selectedBatchId.value || !canPromoteSelected.value) return;
  const response = await run(
    () =>
      api.post<PromoteBatchResult>(`/tools/data-extract/batches/${selectedBatchId.value}/promote`),
    { errorFallback: "Promotion failed" },
  );
  if (response) {
    promoteResult.value = response.data;
    await loadBatchHistory();
    await loadBatchDetail(selectedBatchId.value);
  }
}

onMounted(() => {
  void loadBatchHistory();
});

function onFileSelect(event: Event): void {
  const input = event.target as HTMLInputElement;
  if (input.files?.[0]) {
    selectedFile.value = input.files[0];
    resetOutputs();
  }
}

function onDrop(event: DragEvent): void {
  dragOver.value = false;
  if (event.dataTransfer?.files?.[0]) {
    selectedFile.value = event.dataTransfer.files[0];
    resetOutputs();
  }
}

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function serializeResult(): string {
  return result.value ? JSON.stringify(result.value, null, 2) : "";
}

function buildQueryParams(): URLSearchParams {
  const params = new URLSearchParams();
  if (formatChoice.value !== "auto") {
    params.set("format", formatChoice.value);
  } else if (profileChoice.value === "pipe_embed") {
    params.set("format", "delimited");
  }
  if (profileChoice.value === "pipe_embed") {
    params.set("profile", "pipe_embed");
  }
  if (showDelimitedOptions.value && profileChoice.value === "custom") {
    if (fieldDelimiter.value.trim()) {
      params.set("field_delimiter", fieldDelimiter.value);
    }
    if (listDelimiter.value.trim()) {
      params.set("list_delimiter", listDelimiter.value);
    }
  }
  if (showXmlOptions.value && rowTag.value.trim()) {
    params.set("row_tag", rowTag.value.trim());
  }
  if (showXmlOptions.value) {
    params.set("xml_mode", xmlMode.value);
  }
  return params;
}

function buildUrl(path: string): string {
  const query = buildQueryParams().toString();
  return query ? `${path}?${query}` : path;
}

async function extractFile(): Promise<void> {
  if (!selectedFile.value) return;

  const response = await run(
    () => {
      const form = new FormData();
      form.append("file", selectedFile.value as File);
      return api.post<ExtractionResult>(buildUrl("/tools/data-extract"), form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    },
    { errorFallback: "Extraction failed" },
  );

  if (response) {
    result.value = response.data;
    importResult.value = null;
    showRawJson.value = false;
  }
}

async function importFile(): Promise<void> {
  if (!selectedFile.value || !canWrite.value) return;

  const response = await run(
    () => {
      const form = new FormData();
      form.append("file", selectedFile.value as File);
      return api.post<ImportResult>(buildUrl("/tools/data-extract/import"), form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    },
    { errorFallback: "Import failed" },
  );

  if (response) {
    importResult.value = response.data;
    selectedBatchId.value = response.data.batch_id;
    result.value = {
      format: response.data.format as DataExtractFormat,
      records: response.data.preview,
      meta: {
        row_count: response.data.row_count,
        error_count: response.data.error_count,
        profile: response.data.profile,
      },
    };
    showRawJson.value = false;
    await loadBatchHistory();
    await loadBatchDetail(response.data.batch_id);
  }
}

async function copyResult(): Promise<void> {
  const json = serializeResult();
  if (!json) return;
  await copy(json);
}

function downloadResult(): void {
  if (!result.value) return;
  const blob = new Blob([serializeResult()], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `extract-${result.value.format}.json`;
  anchor.click();
  URL.revokeObjectURL(url);
}
</script>

<template>
  <AdminPageLayout title="data extract">
    <p class="text-surface-mid text-sm mb-6">
      Upload CSV, JSON, XML, or delimited text. Preview records or import them into staging storage.
    </p>

    <div
      :class="[
        'border-2 border-dashed rounded-lg p-8 text-center mb-6 transition-colors cursor-pointer',
        dragOver
          ? 'border-accent-blue bg-accent-blue/10'
          : 'border-surface-border hover:border-accent-blue',
      ]"
      @dragover.prevent="dragOver = true"
      @dragleave="dragOver = false"
      @drop.prevent="onDrop"
      @click="fileInputRef?.click()"
    >
      <input
        ref="fileInputRef"
        type="file"
        class="hidden"
        accept=".csv,.tsv,.json,.xml,.txt,.pipe"
        @change="onFileSelect"
      />
      <p v-if="selectedName" class="text-surface-light text-sm">{{ selectedName }}</p>
      <p v-else class="text-surface-mid text-sm">Drop a file here or click to browse</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <label class="flex flex-col gap-2 text-sm text-surface-mid">
        Format
        <select v-model="formatChoice" :class="SELECT_CLASS">
          <option value="auto">Auto</option>
          <option value="csv">CSV</option>
          <option value="json">JSON</option>
          <option value="xml">XML</option>
          <option value="delimited">Delimited</option>
        </select>
      </label>

      <label v-if="showDelimitedOptions" class="flex flex-col gap-2 text-sm text-surface-mid">
        Profile
        <select v-model="profileChoice" :class="SELECT_CLASS">
          <option value="custom">Custom delimiters</option>
          <option value="pipe_embed">Pipe embed (13 fields)</option>
        </select>
      </label>

      <label
        v-if="showDelimitedOptions && profileChoice === 'custom'"
        class="flex flex-col gap-2 text-sm text-surface-mid"
      >
        Field delimiter
        <input
          v-model="fieldDelimiter"
          type="text"
          maxlength="4"
          class="rounded-md border border-surface-border bg-surface-dark px-3 py-2 text-surface-light"
        />
      </label>

      <label
        v-if="showDelimitedOptions && profileChoice === 'custom'"
        class="flex flex-col gap-2 text-sm text-surface-mid"
      >
        List delimiter
        <input
          v-model="listDelimiter"
          type="text"
          maxlength="4"
          class="rounded-md border border-surface-border bg-surface-dark px-3 py-2 text-surface-light"
        />
      </label>

      <label v-if="showXmlOptions" class="flex flex-col gap-2 text-sm text-surface-mid">
        XML row tag
        <input
          v-model="rowTag"
          type="text"
          placeholder="item (optional)"
          class="rounded-md border border-surface-border bg-surface-dark px-3 py-2 text-surface-light"
        />
      </label>

      <label v-if="showXmlOptions" class="flex flex-col gap-2 text-sm text-surface-mid">
        XML mode
        <select v-model="xmlMode" :class="SELECT_CLASS">
          <option value="rows">Rows</option>
          <option value="tree">Tree</option>
        </select>
      </label>
    </div>

    <div class="flex flex-wrap gap-3 mb-10">
      <BaseButton variant="primary" :disabled="loading || !selectedFile" @click="extractFile">
        {{ loading ? "Working..." : "Extract" }}
      </BaseButton>
      <BaseButton
        v-if="canWrite"
        variant="secondary"
        :disabled="loading || !selectedFile"
        @click="importFile"
      >
        {{ loading ? "Working..." : "Import to DB" }}
      </BaseButton>
    </div>

    <BaseCard v-if="batchHistory.length" class="space-y-3 mb-6">
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-lg font-semibold text-surface-light">Recent imports</h2>
        <BaseButton variant="ghost" @click="loadBatchHistory">Refresh</BaseButton>
      </div>
      <ul class="space-y-2">
        <li v-for="batch in batchHistory" :key="batch.id">
          <button
            type="button"
            :class="[
              'w-full text-left rounded-md border px-3 py-2 text-sm transition-colors',
              selectedBatchId === batch.id
                ? 'border-accent-blue bg-accent-blue/10 text-surface-light'
                : 'border-surface-border text-surface-mid hover:border-accent-blue',
            ]"
            @click="loadBatchDetail(batch.id)"
          >
            {{ batchLabel(batch) }}
          </button>
        </li>
      </ul>
    </BaseCard>

    <BaseCard v-if="importResult" class="space-y-3 mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold text-surface-light">Import batch</h2>
          <p class="text-sm text-surface-mid">{{ importSummary }}</p>
          <p v-if="importResult.error_count > 0" class="text-xs text-amber-400">
            {{ importResult.error_count }} row(s) failed parsing and were stored with errors.
          </p>
          <p v-if="selectedBatch?.promoted_count" class="text-xs text-emerald-400 mt-1">
            {{ selectedBatch.promoted_count }} row(s) promoted to embed storage.
          </p>
        </div>
        <BaseButton
          v-if="canPromoteSelected"
          variant="secondary"
          :disabled="loading"
          @click="promoteSelectedBatch"
        >
          {{ loading ? "Working..." : "Promote pipe embed rows" }}
        </BaseButton>
      </div>
      <p v-if="promoteResult" class="text-xs text-surface-mid">
        Promoted {{ promoteResult.promoted }}, skipped {{ promoteResult.skipped }}
        <span v-if="promoteResult.errors.length">, {{ promoteResult.errors.length }} error(s)</span
        >.
      </p>
    </BaseCard>

    <BaseCard v-if="result" class="space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold text-surface-light">Results</h2>
          <p class="text-xs text-surface-mid mt-1">{{ metaSummary }}</p>
        </div>
        <div class="flex gap-2">
          <BaseButton variant="ghost" @click="copyResult">Copy JSON</BaseButton>
          <BaseButton variant="ghost" @click="downloadResult">Download JSON</BaseButton>
          <BaseButton variant="ghost" @click="showRawJson = !showRawJson">
            {{ showRawJson ? "Hide raw JSON" : "Show raw JSON" }}
          </BaseButton>
        </div>
      </div>

      <div v-if="tableRows.length && tableColumns.length" class="overflow-x-auto">
        <table class="min-w-full text-sm text-left">
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
                {{ formatCell(row[column]) }}
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="tableRows.length > 50" class="text-xs text-surface-mid mt-2">
          Showing first 50 of {{ tableRows.length }} rows.
        </p>
      </div>

      <div
        v-if="importResult?.errors.length"
        class="rounded-md border border-amber-500/40 bg-amber-500/5 p-4 space-y-2"
      >
        <h3 class="text-sm font-medium text-amber-300">Parse errors</h3>
        <ul class="text-xs text-surface-mid space-y-1">
          <li v-for="(error, index) in importResult.errors.slice(0, 10)" :key="index">
            Line {{ error.line_number ?? "?" }}: {{ error.message }}
          </li>
        </ul>
      </div>

      <pre
        v-if="showRawJson"
        class="overflow-x-auto rounded-md bg-surface-dark border border-surface-border p-4 text-xs text-surface-light"
        >{{ resultJson }}</pre
      >
    </BaseCard>
  </AdminPageLayout>
</template>
