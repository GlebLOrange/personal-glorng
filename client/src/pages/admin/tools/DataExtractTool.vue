<script setup lang="ts">
import DataExtractBatchPanel from "@/components/admin/data-extract/DataExtractBatchPanel.vue";
import DataExtractOptionsPanel from "@/components/admin/data-extract/DataExtractOptionsPanel.vue";
import DataExtractResultPanel from "@/components/admin/data-extract/DataExtractResultPanel.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import CollapsibleUsageGuide from "@/components/ui/CollapsibleUsageGuide.vue";
import FileDropZone from "@/components/ui/FileDropZone.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { useDataExtractTool } from "@/composables/useDataExtractTool";

const ACCEPT_EXTS = ["csv", "tsv", "json", "xml", "txt", "pipe"] as const;
const acceptAttr = ACCEPT_EXTS.map((ext) => `.${ext}`).join(",");
const acceptHint = `${ACCEPT_EXTS.slice(0, -1)
  .map((ext) => ext.toUpperCase())
  .join(", ")}, or ${ACCEPT_EXTS[ACCEPT_EXTS.length - 1].toUpperCase()}`;

const {
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
} = useDataExtractTool();
</script>

<template>
  <AdminPageLayout hub="tools" title="data extract">
    <div class="min-w-0">
      <CollapsibleUsageGuide title="data extract usage guide" class="mb-6">
        <div class="space-y-4 text-sm text-surface-light">
          <p class="text-surface-mid">
            Extract structured rows from CSV, JSON, XML, and delimited files.
          </p>

          <div>
            <h3 class="mb-2 font-bold text-accent-blue">Formats</h3>
            <p class="text-surface-mid">
              Accepted types are listed on the drop zone. Use options to override auto format
              detection.
            </p>
          </div>

          <div>
            <h3 class="mb-2 font-bold text-accent-blue">Delimited &amp; pipe embed</h3>
            <p class="text-surface-mid">
              Configure delimiters and pipe-embed profile in options. Promote moves staged
              pipe-embed rows into embed storage.
            </p>
          </div>

          <div>
            <h3 class="mb-2 font-bold text-accent-blue">XML</h3>
            <p class="text-surface-mid">
              Set row tag and rows/tree mode in options when format is XML.
            </p>
          </div>

          <div>
            <h3 class="mb-2 font-bold text-accent-blue">Workflow</h3>
            <ul class="ml-2 list-inside list-disc space-y-1 text-surface-mid">
              <li>
                <code class="text-surface-light">extract</code> — preview rows in the browser (no
                DB write)
              </li>
              <li>
                <code class="text-surface-light">import to db</code> — stage rows in an import batch
              </li>
              <li>
                <code class="text-surface-light">promote</code> — push a staged pipe-embed batch into
                embed storage
              </li>
            </ul>
          </div>
        </div>
      </CollapsibleUsageGuide>

      <div class="mb-6 space-y-3">
        <div class="flex w-full min-w-0 flex-wrap items-center gap-2">
          <DataExtractOptionsPanel
            v-model:format-choice="formatChoice"
            v-model:profile-choice="profileChoice"
            v-model:field-delimiter="fieldDelimiter"
            v-model:list-delimiter="listDelimiter"
            v-model:row-tag="rowTag"
            v-model:xml-mode="xmlMode"
            :has-custom-options="hasCustomOptions"
            :options-active-label="optionsActiveLabel"
            :show-delimited-options="showDelimitedOptions"
            :show-xml-options="showXmlOptions"
          />

          <div class="ml-auto flex flex-wrap items-center gap-1">
            <ToolbarPillButton
              v-if="canWrite"
              family="3xx"
              type="button"
              :disabled="loading || !selectedFile"
              @click="
                activeTab = 'import';
                void importFile();
              "
            >
              {{ loading && activeTab === "import" ? "working…" : "import to db" }}
            </ToolbarPillButton>
            <ToolbarPillButton
              family="2xx"
              type="button"
              :disabled="loading || !selectedFile"
              @click="
                activeTab = 'extract';
                void extractFile();
              "
            >
              {{ loading && activeTab === "extract" ? "working…" : "extract" }}
            </ToolbarPillButton>
          </div>
        </div>

        <FileDropZone
          aria-label="Choose a file to extract"
          :accept="acceptAttr"
          :hint="acceptHint"
          :selected-name="selectedName"
          @select="selectFile"
        />
      </div>

      <DataExtractBatchPanel
        :batch-history="batchHistory"
        :batch-total="batchTotal"
        :batch-page="batchPage"
        :batch-total-pages="batchTotalPages"
        :has-next-batch-page="hasNextBatchPage"
        :has-previous-batch-page="hasPreviousBatchPage"
        :selected-batch-id="selectedBatchId"
        :import-result="importResult"
        :import-summary="importSummary"
        :selected-batch="selectedBatch"
        :can-promote-selected="canPromoteSelected"
        :promote-result="promoteResult"
        :loading="loading"
        @refresh="loadBatchHistory"
        @select="loadBatchDetail"
        @promote="promoteSelectedBatch"
        @first="goToBatchPage(1)"
        @prev="goToBatchPage(batchPage - 1)"
        @next="goToBatchPage(batchPage + 1)"
        @last="goToBatchPage(batchTotalPages)"
      />

      <DataExtractResultPanel
        v-if="result"
        v-model:show-raw-json="showRawJson"
        :result="result"
        :import-result="importResult"
        :meta-summary="metaSummary"
        :table-columns="tableColumns"
        :table-rows="tableRows"
        :result-json="resultJson"
        @copy="copyResult"
        @download="downloadResult"
      />
    </div>
  </AdminPageLayout>
</template>
