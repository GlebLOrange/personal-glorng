<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from "vue";
import axios from "axios";

import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import PageShell from "@/components/layout/PageShell.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import FileDropZone from "@/components/ui/FileDropZone.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconCopyButton from "@/components/ui/IconCopyButton.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import {
  ADMIN_ACTIONS_CLASS,
  ADMIN_TD_ACTIONS_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TH_CLASS,
  ADMIN_TH_ROW_CLASS,
  ADMIN_TR_CLASS,
} from "@/constants/adminDataTable";
import { LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import { useNotify } from "@/composables/useNotify";
import type { PaginatedList, SharedFile } from "@/types";
import { getApiErrorMessage } from "@/types/api";
import { formatBytes, formatTimeRemaining } from "@/utils/format";
import { publicUrl } from "@/utils/publicLinks";

const files = ref<SharedFile[]>([]);
const page = ref(1);
const total = ref(0);
const totalPages = ref(0);
const selectedFile = ref<File | null>(null);
const toolDisabled = ref(false);
const listLoading = ref(false);
const { copy } = useClipboard();
const { toast } = useNotify();
const { loading: uploading, run: runUpload } = useApiAction();
const { run: runDelete } = useApiAction();

const dropZoneRef = useTemplateRef<{ clear: () => void }>("dropZone");

const selectedName = computed(() => selectedFile.value?.name ?? "");

const hasNextPage = computed(() => page.value < totalPages.value);
const hasPreviousPage = computed(() => page.value > 1);

async function loadFiles(): Promise<void> {
  listLoading.value = true;
  try {
    const { data } = await api.get<PaginatedList<SharedFile>>("/tools/file-share", {
      params: { page: page.value, per_page: LIST_PAGE_SIZE },
    });
    toolDisabled.value = false;
    files.value = data.items;
    total.value = data.total;
    totalPages.value = data.pages;
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 404) {
      toolDisabled.value = true;
      return;
    }
    toast(getApiErrorMessage(err, "Failed to load files"), "error");
  } finally {
    listLoading.value = false;
  }
}

function goToPage(nextPage: number): void {
  if (nextPage < 1) return;
  if (totalPages.value > 0 && nextPage > totalPages.value) return;
  page.value = nextPage;
  void loadFiles();
}

function onSelectFile(file: File): void {
  selectedFile.value = file;
}

async function upload(): Promise<void> {
  if (!selectedFile.value) return;
  const file = selectedFile.value;
  const result = await runUpload(
    () => {
      const form = new FormData();
      form.append("file", file);
      return api.post("/tools/file-share", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    },
    { successMessage: "File uploaded", errorFallback: "Upload failed" },
  );
  if (result) {
    selectedFile.value = null;
    dropZoneRef.value?.clear();
    page.value = 1;
    await loadFiles();
  }
}

async function deleteFile(id: number): Promise<void> {
  const result = await runDelete(() => api.delete(`/tools/file-share/${id}`), {
    successMessage: "File deleted",
    errorFallback: "Failed to delete file",
  });
  if (result) {
    await loadFiles();
  }
}

function shareLink(file: SharedFile): string {
  return publicUrl("f", file.code);
}

onMounted(loadFiles);
</script>

<template>
  <PageShell
    title="file share"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'file share' }]"
    back-to="/tools"
    max-width="5xl"
    :narrow="false"
    tool
  >
    <p
      v-if="toolDisabled"
      class="mb-4 rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm text-surface-sage"
      role="status"
    >
      This tool is turned off on this server.
    </p>
    <template v-if="!toolDisabled">
      <div class="page-tool-actions mb-10">
        <div class="flex items-center justify-center gap-2">
          <ToolbarPillButton
            action="save"
            class="w-auto"
            :disabled="uploading || !selectedFile"
            @click="upload"
          >
            {{ uploading ? "uploading…" : "upload & share" }}
          </ToolbarPillButton>
        </div>

        <FileDropZone
          ref="dropZone"
          class="w-auto max-w-full"
          aria-label="choose a file to share"
          :selected-name="selectedName"
          @select="onSelectFile"
        />
      </div>

      <div class="w-full min-w-0 self-stretch">
        <AdminListSkeleton v-if="listLoading" label="loading shared files" />

        <template v-else>
          <AdminDataTable v-if="files.length > 0" table-label="shared files">
            <template #header>
              <th :class="ADMIN_TH_CLASS" scope="col">file</th>
              <th :class="ADMIN_TH_CLASS" scope="col">link</th>
              <th :class="ADMIN_TH_CLASS" scope="col">size</th>
              <th :class="[ADMIN_TH_CLASS, 'text-right']" scope="col">downloads</th>
              <th :class="ADMIN_TH_CLASS" scope="col">expires</th>
              <th :class="[ADMIN_TH_CLASS, 'w-px text-right']" scope="col">actions</th>
            </template>
            <tr v-for="f in files" :key="f.id" :class="ADMIN_TR_CLASS">
              <th :class="ADMIN_TH_ROW_CLASS" scope="row">
                <p class="truncate text-sm text-surface-light" :title="f.original_filename">
                  {{ f.original_filename }}
                </p>
              </th>
              <td :class="ADMIN_TD_CLASS">
                <code class="text-link block max-w-[14rem] truncate text-xs" :title="shareLink(f)">
                  {{ shareLink(f) }}
                </code>
              </td>
              <td :class="ADMIN_TD_MUTED_CLASS">{{ formatBytes(f.file_size) }}</td>
              <td :class="[ADMIN_TD_MUTED_CLASS, 'text-right tabular-nums']">{{ f.downloads }}</td>
              <td :class="ADMIN_TD_MUTED_CLASS">{{ formatTimeRemaining(f.expires_at) }}</td>
              <td :class="ADMIN_TD_ACTIONS_CLASS">
                <div :class="ADMIN_ACTIONS_CLASS">
                  <IconCopyButton
                    :aria-label="`copy link for ${f.original_filename}`"
                    @click="copy(shareLink(f))"
                  />
                  <IconCloseButton
                    :aria-label="`delete ${f.original_filename}`"
                    @click="deleteFile(f.id)"
                  />
                </div>
              </td>
            </tr>
          </AdminDataTable>

          <EmptyState
            v-else
            title="no shared files"
            description="upload a file above to get a shareable link"
          />

          <AdminListFooter
            v-if="files.length > 0"
            :total="total"
            :page="page"
            :total-pages="totalPages"
            :has-next-page="hasNextPage"
            :has-previous-page="hasPreviousPage"
            :loading="listLoading"
            item-label="files"
            aria-label="shared files pagination"
            @first="goToPage(1)"
            @prev="goToPage(page - 1)"
            @next="goToPage(page + 1)"
            @last="goToPage(totalPages)"
          />
        </template>
      </div>
    </template>
  </PageShell>
</template>
