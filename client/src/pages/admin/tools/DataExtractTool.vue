<script setup lang="ts">
import { computed, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import { SELECT_CLASS } from "@/constants/formClasses";
import type { DataExtractFormat, ExtractionResult, XmlExtractMode } from "@/types/dataExtract";

type FormatChoice = "auto" | DataExtractFormat;

const selectedFile = ref<File | null>(null);
const dragOver = ref(false);
const formatChoice = ref<FormatChoice>("auto");
const rowTag = ref("");
const xmlMode = ref<XmlExtractMode>("rows");
const showRawJson = ref(false);
const result = ref<ExtractionResult | null>(null);

const fileInputRef = ref<HTMLInputElement | null>(null);
const { loading, run } = useApiAction();
const { copy } = useClipboard();

const selectedName = computed(() => selectedFile.value?.name ?? "");
const showXmlOptions = computed(
  () => formatChoice.value === "auto" || formatChoice.value === "xml",
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
  if (typeof meta.filename === "string") {
    parts.push(String(meta.filename));
  }
  return parts.join(" · ");
});

const tableColumns = computed((): string[] => {
  if (!result.value) return [];
  const metaColumns = result.value.meta.columns;
  if (Array.isArray(metaColumns) && metaColumns.every((c) => typeof c === "string")) {
    return metaColumns as string[];
  }
  const first = result.value.records[0];
  if (first && typeof first === "object" && !Array.isArray(first)) {
    return Object.keys(first as Record<string, unknown>);
  }
  return [];
});

const tableRows = computed((): Record<string, unknown>[] => {
  if (!result.value || !tableColumns.value.length) return [];
  return result.value.records.filter(
    (row): row is Record<string, unknown> =>
      typeof row === "object" && row !== null && !Array.isArray(row),
  );
});

const resultJson = computed(() =>
  result.value ? JSON.stringify(result.value, null, 2) : "",
);

function onFileSelect(event: Event): void {
  const input = event.target as HTMLInputElement;
  if (input.files?.[0]) {
    selectedFile.value = input.files[0];
    result.value = null;
  }
}

function onDrop(event: DragEvent): void {
  dragOver.value = false;
  if (event.dataTransfer?.files?.[0]) {
    selectedFile.value = event.dataTransfer.files[0];
    result.value = null;
  }
}

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

async function extractFile(): Promise<void> {
  if (!selectedFile.value) return;

  const params = new URLSearchParams();
  if (formatChoice.value !== "auto") {
    params.set("format", formatChoice.value);
  }
  if (showXmlOptions.value && rowTag.value.trim()) {
    params.set("row_tag", rowTag.value.trim());
  }
  if (showXmlOptions.value) {
    params.set("xml_mode", xmlMode.value);
  }

  const query = params.toString();
  const url = query ? `/tools/data-extract?${query}` : "/tools/data-extract";

  const response = await run(
    () => {
      const form = new FormData();
      form.append("file", selectedFile.value as File);
      return api.post<ExtractionResult>(url, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    },
    { errorFallback: "Extraction failed" },
  );

  if (response) {
    result.value = response.data;
    showRawJson.value = false;
  }
}

async function copyResult(): Promise<void> {
  if (!resultJson.value) return;
  await copy(resultJson.value);
}

function downloadResult(): void {
  if (!result.value) return;
  const blob = new Blob([resultJson.value], { type: "application/json" });
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
      Upload CSV, JSON, or XML and preview normalized records.
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
      <input ref="fileInputRef" type="file" class="hidden" accept=".csv,.tsv,.json,.xml" @change="onFileSelect" />
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
        </select>
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

    <BaseButton
      variant="primary"
      :disabled="loading || !selectedFile"
      class="mb-10"
      @click="extractFile"
    >
      {{ loading ? "Extracting..." : "Extract" }}
    </BaseButton>

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

      <pre
        v-if="showRawJson"
        class="overflow-x-auto rounded-md bg-surface-dark border border-surface-border p-4 text-xs text-surface-light"
      >{{ resultJson }}</pre>
    </BaseCard>
  </AdminPageLayout>
</template>
