<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import ShareableListItem from "@/components/admin/ShareableListItem.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BasePagination from "@/components/ui/BasePagination.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import { LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import type { PaginatedList, SharedFile } from "@/types";
import { formatBytes, formatTimeRemaining } from "@/utils/format";
import { publicUrl } from "@/utils/publicLinks";

const files = ref<SharedFile[]>([]);
const page = ref(1);
const totalPages = ref(0);
const selectedFile = ref<File | null>(null);
const dragOver = ref(false);
const { copy } = useClipboard();
const { loading: listLoading, run: runList } = useApiAction();
const { loading: uploading, run: runUpload } = useApiAction();
const { run: runDelete } = useApiAction();

const fileInputRef = ref<HTMLInputElement | null>(null);

const selectedName = computed(() => selectedFile.value?.name ?? "");

const hasNextPage = computed(() => page.value < totalPages.value);
const hasPreviousPage = computed(() => page.value > 1);

async function loadFiles(): Promise<void> {
  const data = await runList(
    () =>
      api.get<PaginatedList<SharedFile>>("/tools/file-share", {
        params: { page: page.value, per_page: LIST_PAGE_SIZE },
      }),
    {
      errorFallback: "Failed to load files",
    },
  );
  if (data) {
    files.value = data.data.items;
    totalPages.value = data.data.pages;
  }
}

function goToPage(nextPage: number): void {
  if (nextPage < 1) return;
  if (totalPages.value > 0 && nextPage > totalPages.value) return;
  page.value = nextPage;
  void loadFiles();
}

function onFileSelect(e: Event): void {
  const input = e.target as HTMLInputElement;
  if (input.files?.[0]) selectedFile.value = input.files[0];
}

function onDrop(e: DragEvent): void {
  dragOver.value = false;
  if (e.dataTransfer?.files?.[0]) selectedFile.value = e.dataTransfer.files[0];
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
    if (fileInputRef.value) fileInputRef.value.value = "";
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

function fileMeta(file: SharedFile): string {
  const expiry = formatTimeRemaining(file.expires_at);
  return `${formatBytes(file.file_size)} · ${file.downloads} downloads · ${expiry}`;
}

onMounted(loadFiles);
</script>

<template>
  <AdminPageLayout title="file-share">
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
      <input ref="fileInputRef" type="file" class="hidden" @change="onFileSelect" />
      <p v-if="selectedName" class="text-surface-light text-sm">
        {{ selectedName }}
      </p>
      <p v-else class="text-surface-mid text-sm">Drop a file here or click to browse</p>
    </div>

    <BaseButton
      variant="primary"
      :disabled="uploading || !selectedFile"
      class="mb-10"
      @click="upload"
    >
      {{ uploading ? "Uploading..." : "Upload & Share" }}
    </BaseButton>

    <div class="space-y-3">
      <div v-if="listLoading" class="space-y-3" aria-busy="true" aria-label="Loading shared files">
        <Card v-for="n in 3" :key="n" variant="compact" class="animate-pulse">
          <div class="h-4 w-48 bg-surface-border rounded mb-2" />
          <div class="h-3 w-32 bg-surface-border rounded" />
        </Card>
      </div>

      <template v-else>
        <ShareableListItem
          v-for="f in files"
          :key="f.id"
          :title="f.original_filename"
          :link="publicUrl('f', f.code)"
          :meta="fileMeta(f)"
          @copy="copy(publicUrl('f', f.code))"
          @delete="deleteFile(f.id)"
        />

        <EmptyState
          v-if="files.length === 0"
          title="No shared files"
          description="Upload a file above to get a shareable link."
        />

        <BasePagination
          v-if="totalPages > 1"
          class="pt-2"
          aria-label="Shared files pagination"
          :page="page"
          :total-pages="totalPages"
          :has-next-page="hasNextPage"
          :has-previous-page="hasPreviousPage"
          :loading="listLoading"
          @prev="goToPage(page - 1)"
          @next="goToPage(page + 1)"
        />
      </template>
    </div>
  </AdminPageLayout>
</template>
