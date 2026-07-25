<script setup lang="ts">
import { ref } from "vue";

import DataExtractBatchPanel from "@/components/admin/data-extract/DataExtractBatchPanel.vue";
import DataExtractOptionsPanel from "@/components/admin/data-extract/DataExtractOptionsPanel.vue";
import DataExtractResultPanel from "@/components/admin/data-extract/DataExtractResultPanel.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { useDataExtractTool } from "@/composables/useDataExtractTool";

const guideOpen = ref(false);

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
      <BaseButton
        variant="ghost"
        size="sm"
        class="mb-4"
        @click="guideOpen = !guideOpen"
      >
        {{ guideOpen ? "▾ Hide" : "▸ Show" }} data extract usage guide
      </BaseButton>

      <Card v-if="guideOpen" class="mb-6">
        <div class="space-y-4 text-sm text-surface-light">
          <p class="text-surface-mid">
            Extract structured rows from CSV, JSON, XML, and delimited files.
          </p>

          <div>
            <h3 class="mb-2 font-bold text-accent-blue">Formats</h3>
            <p class="text-surface-mid">
              Accepts CSV, TSV, JSON, XML, TXT, and PIPE. Leave format on
              <code class="text-surface-light">auto</code> to detect from the extension, or override
              in options.
            </p>
          </div>

          <div>
            <h3 class="mb-2 font-bold text-accent-blue">Delimited &amp; pipe embed</h3>
            <p class="text-surface-mid">
              Field delimiter separates columns; list delimiter splits values inside one cell.
              <code class="text-surface-light">pipe embed</code> is a preset (
              <code class="text-surface-light">|</code> fields,
              <code class="text-surface-light">;</code> lists). Promote moves staged pipe-embed rows
              into embed storage.
            </p>
          </div>

          <div>
            <h3 class="mb-2 font-bold text-accent-blue">XML</h3>
            <p class="text-surface-mid">
              Set the repeating element as the row tag (e.g.
              <code class="text-surface-light">item</code>).
              <code class="text-surface-light">rows</code> flattens to a table;
              <code class="text-surface-light">tree</code> keeps nested JSON.
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
      </Card>

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

        <div
          role="button"
          tabindex="0"
          aria-label="Choose a file to extract"
          :aria-describedby="selectedName ? undefined : 'data-extract-drop-hint'"
          :class="[
            'cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-colors',
            dragOver
              ? 'border-accent-blue bg-accent-blue/10'
              : 'border-surface-border hover:border-accent-blue',
          ]"
          @dragover.prevent="dragOver = true"
          @dragleave="dragOver = false"
          @drop.prevent="onDrop"
          @click="fileInputRef?.click()"
          @keydown.enter.prevent="fileInputRef?.click()"
          @keydown.space.prevent="fileInputRef?.click()"
        >
          <input
            ref="fileInputRef"
            type="file"
            class="hidden"
            accept=".csv,.tsv,.json,.xml,.txt,.pipe"
            @change="onFileSelect"
          />
          <p v-if="selectedName" class="text-sm text-surface-light">{{ selectedName }}</p>
          <template v-else>
            <p class="text-sm text-surface-mid">drop a file here or click to browse</p>
            <p id="data-extract-drop-hint" class="mt-1 text-xs text-surface-mid">
              CSV, TSV, JSON, XML, TXT, or PIPE
            </p>
          </template>
        </div>
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
