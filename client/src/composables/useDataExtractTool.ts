import { computed, onMounted, ref, watch } from "vue";

import { LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import { usePermissions } from "@/composables/usePermissions";
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
import type { PaginatedList } from "@/types";

export type FormatChoice = "auto" | DataExtractFormat;
export type ActionTab = "extract" | "import";

export function buildDataExtractQueryParams(options: {
  formatChoice: FormatChoice;
  profileChoice: DelimitedProfile;
  fieldDelimiter: string;
  listDelimiter: string;
  rowTag: string;
  xmlMode: XmlExtractMode;
  showDelimitedOptions: boolean;
  showXmlOptions: boolean;
}): URLSearchParams {
  const params = new URLSearchParams();
  if (options.formatChoice !== "auto") {
    params.set("format", options.formatChoice);
  } else if (options.profileChoice === "pipe_embed") {
    params.set("format", "delimited");
  }
  if (options.profileChoice === "pipe_embed") {
    params.set("profile", "pipe_embed");
  }
  if (options.showDelimitedOptions && options.profileChoice === "custom") {
    if (options.fieldDelimiter.trim()) {
      params.set("field_delimiter", options.fieldDelimiter);
    }
    if (options.listDelimiter.trim()) {
      params.set("list_delimiter", options.listDelimiter);
    }
  }
  if (options.showXmlOptions && options.rowTag.trim()) {
    params.set("row_tag", options.rowTag.trim());
  }
  if (options.showXmlOptions) {
    params.set("xml_mode", options.xmlMode);
  }
  return params;
}

export function formatDataExtractCell(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function batchLabel(batch: ImportBatchSummary): string {
  const parts = [`#${batch.id}`, batch.filename, `${batch.row_count} rows`, batch.status];
  if (batch.promoted_count > 0) {
    parts.push(`${batch.promoted_count} promoted`);
  }
  return parts.join(" · ");
}

export function useDataExtractTool() {
  const selectedFile = ref<File | null>(null);
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
  const batchPage = ref(1);
  const batchTotal = ref(0);
  const batchTotalPages = ref(0);
  const selectedBatchId = ref<number | null>(null);
  const batchDetail = ref<ImportBatchDetail | null>(null);
  const promoteResult = ref<PromoteBatchResult | null>(null);
  const activeTab = ref<ActionTab>("extract");

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

  const hasCustomOptions = computed(
    () =>
      formatChoice.value !== "auto" ||
      profileChoice.value !== "custom" ||
      fieldDelimiter.value !== "|" ||
      listDelimiter.value !== ";" ||
      Boolean(rowTag.value.trim()) ||
      xmlMode.value !== "rows",
  );

  const optionsActiveLabel = computed(() => {
    if (formatChoice.value !== "auto") return formatChoice.value;
    if (profileChoice.value === "pipe_embed") return "pipe embed";
    return undefined;
  });

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

  const hasNextBatchPage = computed(() => batchPage.value < batchTotalPages.value);
  const hasPreviousBatchPage = computed(() => batchPage.value > 1);

  function resetOutputs(): void {
    result.value = null;
    importResult.value = null;
    promoteResult.value = null;
  }

  async function loadBatchHistory(): Promise<void> {
    const response = await api.get<PaginatedList<ImportBatchSummary>>(
      "/tools/data-extract/batches",
      {
        params: { page: batchPage.value, per_page: LIST_PAGE_SIZE },
      },
    );
    batchHistory.value = response.data.items;
    batchTotal.value = response.data.total;
    batchTotalPages.value = response.data.pages;
  }

  function goToBatchPage(nextPage: number): void {
    if (nextPage < 1) return;
    if (batchTotalPages.value > 0 && nextPage > batchTotalPages.value) return;
    batchPage.value = nextPage;
    void loadBatchHistory();
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
        api.post<PromoteBatchResult>(
          `/tools/data-extract/batches/${selectedBatchId.value}/promote`,
        ),
      { errorFallback: "Promotion failed" },
    );
    if (response) {
      promoteResult.value = response.data;
      await Promise.all([loadBatchHistory(), loadBatchDetail(selectedBatchId.value)]);
    }
  }

  function selectFile(file: File): void {
    selectedFile.value = file;
    resetOutputs();
  }

  function serializeResult(): string {
    return result.value ? JSON.stringify(result.value, null, 2) : "";
  }

  function buildQueryParams(): URLSearchParams {
    return buildDataExtractQueryParams({
      formatChoice: formatChoice.value,
      profileChoice: profileChoice.value,
      fieldDelimiter: fieldDelimiter.value,
      listDelimiter: listDelimiter.value,
      rowTag: rowTag.value,
      xmlMode: xmlMode.value,
      showDelimitedOptions: showDelimitedOptions.value,
      showXmlOptions: showXmlOptions.value,
    });
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
      await Promise.all([loadBatchHistory(), loadBatchDetail(response.data.batch_id)]);
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

  watch(canWrite, (allowed) => {
    if (!allowed && activeTab.value === "import") activeTab.value = "extract";
  });

  onMounted(() => {
    void loadBatchHistory();
  });

  return {
    selectedFile,
    formatChoice,
    profileChoice,
    fieldDelimiter,
    listDelimiter,
    rowTag,
    xmlMode,
    showRawJson,
    result,
    importResult,
    batchHistory,
    batchPage,
    batchTotal,
    batchTotalPages,
    selectedBatchId,
    batchDetail,
    promoteResult,
    activeTab,
    loading,
    canWrite,
    selectedName,
    selectedBatch,
    canPromoteSelected,
    showXmlOptions,
    showDelimitedOptions,
    hasCustomOptions,
    optionsActiveLabel,
    metaSummary,
    importSummary,
    tableColumns,
    tableRows,
    resultJson,
    hasNextBatchPage,
    hasPreviousBatchPage,
    loadBatchHistory,
    goToBatchPage,
    loadBatchDetail,
    promoteSelectedBatch,
    selectFile,
    extractFile,
    importFile,
    copyResult,
    downloadResult,
    buildQueryParams,
  };
}
