<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import ShareableListItem from "@/components/admin/ShareableListItem.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import type { SharedFile } from "@/types";
import { formatBytes, formatTimeRemaining } from "@/utils/format";
import { publicUrl } from "@/utils/publicLinks";

const files = ref<SharedFile[]>([]);
const selectedFile = ref<File | null>(null);
const dragOver = ref(false);
const { copy } = useClipboard();
const { loading: listLoading, run: runList } = useApiAction();
const { loading: uploading, run: runUpload } = useApiAction();
const { run: runDelete } = useApiAction();

const fileInputRef = ref<HTMLInputElement | null>(null);

const selectedName = computed(() => selectedFile.value?.name ?? "");

async function loadFiles(): Promise<void> {
  const data = await runList(() => api.get<SharedFile[]>("/tools/file-share"), {
    errorFallback: "Failed to load files",
  });
  if (data) {
    files.value = data.data;
  }
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
      <ShareableListItem
        v-for="f in files"
        :key="f.id"
        :title="f.original_filename"
        :link="publicUrl('f', f.code)"
        :meta="fileMeta(f)"
        @copy="copy(publicUrl('f', f.code))"
        @delete="deleteFile(f.id)"
      />

      <EmptyState v-if="files.length === 0 && !listLoading">
        No shared files yet. Upload one above.
      </EmptyState>
    </div>
  </AdminPageLayout>
</template>
