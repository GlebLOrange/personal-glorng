<script setup lang="ts">
import DataExtractBatchPanel from "@/components/admin/data-extract/DataExtractBatchPanel.vue";
import DataExtractOptionsPanel from "@/components/admin/data-extract/DataExtractOptionsPanel.vue";
import DataExtractResultPanel from "@/components/admin/data-extract/DataExtractResultPanel.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { useDataExtractTool } from "@/composables/useDataExtractTool";

const {
  selectedFile,
  dragOver,
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
  fileInputRef,
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
  onFileSelect,
  onDrop,
  extractFile,
  importFile,
  copyResult,
  downloadResult,
} = useDataExtractTool();
</script>

<template>
  <AdminPageLayout hub="tools" title="data extract">
    <div class="min-w-0">
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
              {{ loading && activeTab === "import" ? "working..." : "import to db" }}
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
              {{ loading && activeTab === "extract" ? "working..." : "extract" }}
            </ToolbarPillButton>
          </div>
        </div>

        <label
          :class="[
            'block cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-colors focus-within:ring-2 focus-within:ring-accent-blue/50',
            dragOver
              ? 'border-accent-blue bg-accent-blue/10'
              : 'border-surface-border hover:border-accent-blue',
          ]"
          @dragover.prevent="dragOver = true"
          @dragleave="dragOver = false"
          @drop.prevent="onDrop"
        >
          <input
            ref="fileInputRef"
            type="file"
            class="sr-only"
            accept=".csv,.tsv,.json,.xml,.txt,.pipe"
            @change="onFileSelect"
          />
          <p v-if="selectedName" class="text-sm text-surface-light">{{ selectedName }}</p>
          <p v-else class="text-sm text-surface-mid">drop a file here or click to browse</p>
        </label>
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
