<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { api } from "@/composables/useApi";
import { useClipboard } from "@/composables/useClipboard";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import type { SharedFile } from "@/types";

const files = ref<SharedFile[]>([]);
const selectedFile = ref<File | null>(null);
const uploading = ref(false);
const dragOver = ref(false);
const { toast } = useNotify();
const { copy } = useClipboard();

const fileInputRef = ref<HTMLInputElement | null>(null);

const selectedName = computed(() => selectedFile.value?.name ?? "");

async function loadFiles(): Promise<void> {
  try {
    const { data } = await api.get<SharedFile[]>("/tools/file-share");
    files.value = data;
  } catch (err) {
    console.error(err);
    toast("Failed to load files", "error");
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
  uploading.value = true;
  try {
    const form = new FormData();
    form.append("file", selectedFile.value);
    await api.post("/tools/file-share", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    selectedFile.value = null;
    if (fileInputRef.value) fileInputRef.value.value = "";
    toast("File uploaded", "success");
    await loadFiles();
  } catch (err) {
    toast(getApiErrorMessage(err, "Upload failed"), "error");
  } finally {
    uploading.value = false;
  }
}

async function deleteFile(id: number): Promise<void> {
  try {
    await api.delete(`/tools/file-share/${id}`);
    toast("File deleted", "success");
    await loadFiles();
  } catch (err) {
    console.error(err);
    toast("Failed to delete file", "error");
  }
}

function getDownloadUrl(code: string): string {
  return `${window.location.origin}/f/${code}`;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatExpiry(iso: string): string {
  const diff = new Date(iso).getTime() - Date.now();
  if (diff <= 0) return "Expired";
  const hours = Math.floor(diff / 3600000);
  const mins = Math.floor((diff % 3600000) / 60000);
  if (hours > 0) return `${hours}h ${mins}m left`;
  return `${mins}m left`;
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
      <input
        ref="fileInputRef"
        type="file"
        class="hidden"
        @change="onFileSelect"
      />
      <p v-if="selectedName" class="text-surface-light text-sm font-mono">
        {{ selectedName }}
      </p>
      <p v-else class="text-surface-mid text-sm font-mono">
        Drop a file here or click to browse
      </p>
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
      <BaseCard v-for="f in files" :key="f.id" hoverable>
        <div class="flex justify-between items-start">
          <div class="flex-1 min-w-0">
            <div class="text-surface-light font-bold text-sm truncate">
              {{ f.original_filename }}
            </div>
            <div class="flex items-center gap-3 mt-1 text-xs text-surface-mid">
              <span>{{ formatSize(f.file_size) }}</span>
              <span>{{ f.downloads }} downloads</span>
              <span>{{ formatExpiry(f.expires_at) }}</span>
            </div>
            <code class="text-xs text-accent-blue mt-2 block truncate">
              {{ getDownloadUrl(f.code) }}
            </code>
          </div>
          <div class="flex gap-2 ml-4">
            <BaseButton
              variant="ghost"
              size="sm"
              @click="copy(getDownloadUrl(f.code))"
            >
              Copy
            </BaseButton>
            <BaseButton variant="ghost" size="sm" @click="deleteFile(f.id)">
              Delete
            </BaseButton>
          </div>
        </div>
      </BaseCard>

      <p
        v-if="files.length === 0"
        class="text-surface-mid text-sm text-center py-8"
      >
        No shared files yet. Upload one above.
      </p>
    </div>
  </AdminPageLayout>
</template>
