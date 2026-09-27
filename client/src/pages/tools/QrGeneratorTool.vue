<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import QrLibraryListItem from "@/components/admin/QrLibraryListItem.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useQrLibrary } from "@/composables/useQrLibrary";
import type { QrErrorLevel, QrGenerateResponse, QrListItem, QrStoredItem } from "@/types";

const route = useRoute();
const content = ref("");
const label = ref("");
const errorLevel = ref<QrErrorLevel>("M");
const generated = ref<QrGenerateResponse | null>(null);
const editingId = ref<number | null>(null);
const deletingId = ref<number | null>(null);

const {
  canReadLibrary,
  canWriteLibrary,
  loadOne,
  loadList,
  remove,
  items,
  page,
  total,
  totalPages,
  loading: listLoading,
  detailLoading,
  deleting,
  hasNextPage,
  hasPreviousPage,
  goToPage,
} = useQrLibrary();

const { loading: creating, run: runCreate } = useApiAction();
const { loading: savingLibrary, run: runSaveLibrary } = useApiAction();

const canCreate = computed(() => Boolean(content.value.trim()) && !creating.value);
const canSaveLibrary = computed(
  () => canWriteLibrary.value && Boolean(content.value.trim()) && !savingLibrary.value,
);
const isEditing = computed(() => editingId.value != null);

function payloadBody() {
  return {
    content: content.value.trim(),
    label: label.value.trim() || null,
    error_level: errorLevel.value,
  };
}

function applyStored(item: QrStoredItem, svg?: string | null): void {
  editingId.value = item.id;
  content.value = item.content;
  label.value = item.label ?? "";
  errorLevel.value = item.error_level;
  const resolvedSvg = svg ?? item.svg ?? null;
  if (resolvedSvg) {
    generated.value = {
      content_preview: item.content_preview,
      label: item.label,
      error_level: item.error_level,
      svg: resolvedSvg,
    };
  }
}

function clearEditSession(): void {
  editingId.value = null;
  content.value = "";
  label.value = "";
  errorLevel.value = "M";
  generated.value = null;
}

async function openSaved(id: number): Promise<void> {
  if (!canReadLibrary.value) return;
  const item = await loadOne(id);
  if (!item) return;
  applyStored(item);
}

async function loadSavedFromQuery(): Promise<void> {
  const raw = route.query.saved;
  const id = typeof raw === "string" ? Number.parseInt(raw, 10) : Number.NaN;
  if (!Number.isFinite(id) || id < 1) return;
  await openSaved(id);
}

async function createQr(): Promise<void> {
  if (!content.value.trim()) return;
  editingId.value = null;
  const result = await runCreate(
    () => api.post<QrGenerateResponse>("/tools/qr-generator", payloadBody()),
    { successMessage: "QR code generated", errorFallback: "Failed to generate QR code" },
  );
  if (result) {
    generated.value = result.data;
  }
}

async function saveToLibrary(): Promise<void> {
  if (!canWriteLibrary.value || !content.value.trim()) return;
  const isUpdate = editingId.value != null;
  const result = await runSaveLibrary(
    () =>
      isUpdate
        ? api.patch<QrStoredItem>(`/tools/qr-generator/library/${editingId.value}`, payloadBody())
        : api.post<QrStoredItem>("/tools/qr-generator/library", payloadBody()),
    {
      successMessage: isUpdate ? "Saved QR updated" : "QR saved to library",
      errorFallback: "Failed to save QR code",
    },
  );
  if (result) {
    applyStored(result.data, result.data.svg);
    page.value = 1;
    await loadList();
  }
}

async function selectSaved(item: QrListItem): Promise<void> {
  await openSaved(item.id);
}

async function deleteSaved(id: number): Promise<void> {
  deletingId.value = id;
  const ok = await remove(id);
  deletingId.value = null;
  if (!ok) return;
  if (editingId.value === id) clearEditSession();
  await loadList();
}

/** data: URL — CSP img-src allows data:, not blob:. */
const previewUrl = computed(() => {
  const svg = generated.value?.svg;
  if (!svg) return "";
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
});

function downloadSvg(): void {
  if (!previewUrl.value) return;
  const anchor = document.createElement("a");
  anchor.href = previewUrl.value;
  anchor.download = "qr-code.svg";
  anchor.click();
}

const previewAlt = computed(
  () => generated.value?.label || generated.value?.content_preview || "QR code preview",
);

onMounted(() => {
  void loadSavedFromQuery();
  if (canReadLibrary.value) void loadList();
});
</script>

<template>
  <PageShell
    title="qr generator"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'qr generator' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
    <p class="mb-4 text-sm text-surface-mid">
      Quick generate does not store anything on the server — download the SVG if you need it later.
      <span v-if="canWriteLibrary">
        Save to your library to reuse codes (your list only).
      </span>
    </p>

    <div class="grid min-w-0 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,280px)]">
      <Card variant="ghost" class="min-w-0">
        <form class="space-y-3" @submit.prevent="createQr">
          <BaseTextarea
            v-model="content"
            label="payload"
            :rows="4"
            maxlength="2000"
            placeholder="URL, text, Wi‑Fi string, etc."
          />
          <div class="flex flex-wrap gap-3">
            <BaseInput
              v-model="label"
              label="label (optional)"
              placeholder="My link"
              class="min-w-0 flex-1"
              maxlength="120"
            />
            <BaseSelect v-model="errorLevel" label="error correction" class="min-w-[10rem]">
              <option value="L">L (~7%)</option>
              <option value="M">M (~15%)</option>
              <option value="Q">Q (~25%)</option>
              <option value="H">H (~30%)</option>
            </BaseSelect>
          </div>
          <div class="flex flex-wrap gap-2">
            <BaseButton variant="primary" type="submit" :disabled="!canCreate">
              {{ creating ? "generating…" : "generate qr" }}
            </BaseButton>
            <BaseButton
              v-if="canWriteLibrary"
              variant="save"
              type="button"
              :disabled="!canSaveLibrary"
              @click="saveToLibrary"
            >
              {{
                savingLibrary
                  ? "saving…"
                  : isEditing
                    ? "update saved qr"
                    : "save to library"
              }}
            </BaseButton>
            <BaseButton
              v-if="isEditing"
              variant="cancel"
              type="button"
              @click="clearEditSession"
            >
              new / discard
            </BaseButton>
          </div>
          <p v-if="detailLoading" class="text-xs text-surface-mid">Loading saved code…</p>
        </form>
      </Card>

      <Card variant="ghost" class="flex min-h-[280px] flex-col items-center justify-center gap-3 p-4">
        <img
          v-if="previewUrl"
          :src="previewUrl"
          :alt="previewAlt"
          width="256"
          height="256"
          class="max-h-64 max-w-full rounded-md bg-white p-2"
        />
        <p v-else class="text-center text-sm text-surface-mid">
          Generate a code to preview it here.
        </p>
        <BaseButton
          v-if="previewUrl"
          variant="ghost"
          type="button"
          @click="downloadSvg"
        >
          download svg
        </BaseButton>
      </Card>
    </div>

    <section v-if="canReadLibrary" class="mt-8 min-w-0">
      <h2 class="mb-3 text-sm font-medium text-surface-mid">your saved qr codes</h2>
      <AdminListSkeleton v-if="listLoading && items.length === 0" />
      <EmptyState v-else-if="!listLoading && items.length === 0">
        no saved QR codes yet. generate one and save it.
      </EmptyState>
      <div v-else class="min-w-0">
        <QrLibraryListItem
          v-for="item in items"
          :key="item.id"
          :item="item"
          :can-write="canWriteLibrary"
          :deleting="deleting && deletingId === item.id"
          @select="selectSaved(item)"
          @delete="deleteSaved(item.id)"
        />
      </div>
      <AdminListFooter
        v-if="items.length > 0"
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="hasNextPage"
        :has-previous-page="hasPreviousPage"
        :loading="listLoading"
        item-label="QR codes"
        aria-label="your QR codes pagination"
        @first="goToPage(1)"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
        @last="goToPage(totalPages)"
      />
    </section>
  </PageShell>
</template>
