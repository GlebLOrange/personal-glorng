<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import QrLibraryListItem from "@/components/admin/QrLibraryListItem.vue";
import PageShell from "@/components/layout/PageShell.vue";
import DownloadIcon from "@/components/icons/DownloadIcon.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { Card } from "@/components/ui/card";
import { ADMIN_TH_CLASS } from "@/constants/adminDataTable";
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
  isLocalMode,
  canReadLibrary,
  canWriteLibrary,
  guestLimitLabel,
  loadOne,
  loadList,
  remove,
  saveLocal,
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
const saveError = ref("");

const canCreate = computed(() => Boolean(content.value.trim()) && !creating.value);
const canSaveLibrary = computed(
  () =>
    canWriteLibrary.value &&
    Boolean(content.value.trim()) &&
    !savingLibrary.value &&
    !creating.value,
);
const isEditing = computed(() => editingId.value != null);
const pageDescription = computed(() => {
  const base =
    "Quick generate does not store anything on the server — download the SVG if you need it later.";
  if (isLocalMode.value) {
    return `${base} Saved codes stay in this browser.`;
  }
  return canWriteLibrary.value
    ? `${base} Save to your library to reuse codes (your list only).`
    : base;
});

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

async function ensureGeneratedSvg(): Promise<string | null> {
  if (generated.value?.svg) {
    return generated.value.svg;
  }
  if (!content.value.trim()) return null;
  const result = await runCreate(
    () => api.post<QrGenerateResponse>("/tools/qr-generator", payloadBody()),
    { errorFallback: "Failed to generate QR code" },
  );
  if (!result) return null;
  generated.value = result.data;
  return result.data.svg;
}

async function saveToLibrary(): Promise<void> {
  if (!canWriteLibrary.value || !content.value.trim()) return;
  saveError.value = "";
  const isUpdate = editingId.value != null;

  if (isLocalMode.value) {
    const svg = await ensureGeneratedSvg();
    if (!svg) {
      saveError.value = "Generate a QR code before saving";
      return;
    }
    const result = await runSaveLibrary(
      async () => {
        const local = saveLocal({
          id: editingId.value,
          content: content.value.trim(),
          label: label.value.trim() || null,
          error_level: errorLevel.value,
          svg,
        });
        if (!local.ok) {
          throw new Error(local.error);
        }
        return { data: local.item };
      },
      {
        successMessage: isUpdate ? "Saved QR updated" : "QR saved to library",
        errorFallback: "Failed to save QR code",
      },
    );
    if (result) {
      applyStored(result.data, result.data.svg);
    } else {
      saveError.value = "Failed to save QR code";
    }
    return;
  }

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
  if (!content.value.trim()) {
    content.value = `${window.location.origin}/`;
    label.value = "this site";
    void createQr();
  }
  void loadSavedFromQuery();
  if (canReadLibrary.value) void loadList();
});
</script>

<template>
  <PageShell
    title="qr generator"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'qr generator' }]"
    back-to="/tools"
    max-width="5xl"
    body-width="column"
  >
    <div class="flex w-full min-w-0 flex-col gap-6 self-stretch">
      <p class="text-xs text-surface-mid">{{ pageDescription }}</p>
      <div class="grid min-w-0 gap-4 lg:grid-cols-2">
        <div class="page-tool-actions mb-0">
          <Card variant="ghost" class="min-w-0 w-auto max-w-full">
            <form id="qr-generator-form" class="space-y-2" @submit.prevent="createQr">
              <div class="flex flex-wrap gap-2">
                <BaseInput
                  v-model="label"
                  label="label (optional)"
                  placeholder="My link"
                  class="min-w-0"
                  maxlength="120"
                  compact
                  auto-width
                />
                <BaseSelect
                  v-model="errorLevel"
                  label="error correction"
                  class="min-w-[10rem] w-auto"
                  compact
                >
                  <option value="L">L (~7%)</option>
                  <option value="M">M (~15%)</option>
                  <option value="Q">Q (~25%)</option>
                  <option value="H">H (~30%)</option>
                </BaseSelect>
              </div>
              <BaseTextarea
                v-model="content"
                label="payload"
                :rows="2"
                maxlength="2000"
                placeholder="URL, text, Wi‑Fi string, etc."
                compact
                auto-width
              />
              <div class="flex flex-wrap items-center gap-2">
                <BaseButton
                  v-if="isEditing"
                  variant="cancel"
                  type="button"
                  class="w-auto"
                  @click="clearEditSession"
                >
                  new / discard
                </BaseButton>
                <BaseButton
                  v-if="canWriteLibrary"
                  variant="save"
                  type="button"
                  class="w-auto"
                  :disabled="!canSaveLibrary"
                  @click="saveToLibrary"
                >
                  {{ savingLibrary ? "saving…" : isEditing ? "update saved qr" : "save to library" }}
                </BaseButton>
                <BaseButton
                  v-if="previewUrl"
                  variant="ghost"
                  type="button"
                  class="w-auto gap-1.5"
                  @click="downloadSvg"
                >
                  <DownloadIcon class-name="size-3.5 shrink-0" />
                  download svg
                </BaseButton>
                <BaseButton
                  variant="primary"
                  type="submit"
                  :icon="false"
                  class="w-auto gap-1.5"
                  :disabled="!canCreate"
                >
                  <RefreshIcon class-name="size-3.5 shrink-0" />
                  {{ creating ? "generating…" : "generate qr" }}
                </BaseButton>
              </div>
              <p v-if="detailLoading" class="text-xs text-surface-mid">Loading saved code…</p>
              <p v-if="saveError" class="text-xs text-status-error" role="alert">{{ saveError }}</p>
            </form>
          </Card>
        </div>

        <Card
          variant="ghost"
          class="flex w-full max-w-64 shrink-0 flex-col items-stretch self-center p-0 lg:self-start"
        >
          <div class="aspect-square w-full">
            <p
              v-if="!previewUrl"
              class="flex h-full items-center justify-center px-3 text-center text-sm text-surface-mid"
            >
              Generate a code to preview it here.
            </p>
            <img
              v-else
              :src="previewUrl"
              :alt="previewAlt"
              width="256"
              height="256"
              class="h-full w-full rounded-md bg-white p-2 object-contain"
            />
          </div>
        </Card>
      </div>

      <section
        v-if="canReadLibrary"
        class="w-full min-w-0 self-stretch"
        aria-label="saved QR codes"
      >
        <p v-if="guestLimitLabel" class="mb-2 text-xs text-surface-mid" role="status">
          {{ guestLimitLabel }}
        </p>
        <AdminListSkeleton v-if="listLoading && items.length === 0" />
        <p
          v-else-if="!listLoading && items.length === 0"
          class="py-2 text-sm lowercase text-surface-mid"
          role="status"
        >
          no saved QR codes yet. generate one and save it.
        </p>
        <div v-else class="w-full min-w-0 self-stretch">
          <AdminDataTable table-label="saved QR codes">
            <template #header>
              <th :class="ADMIN_TH_CLASS" scope="col">preview</th>
              <th :class="ADMIN_TH_CLASS" scope="col">label</th>
              <th :class="ADMIN_TH_CLASS" scope="col">content</th>
              <th :class="ADMIN_TH_CLASS" scope="col">level</th>
              <th :class="ADMIN_TH_CLASS" scope="col">updated</th>
              <th :class="[ADMIN_TH_CLASS, 'w-px text-right']" scope="col">actions</th>
            </template>
            <QrLibraryListItem
              v-for="item in items"
              :key="item.id"
              :item="item"
              :can-write="canWriteLibrary"
              :deleting="deleting && deletingId === item.id"
              @select="selectSaved(item)"
              @delete="deleteSaved(item.id)"
            />
          </AdminDataTable>
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
    </div>
  </PageShell>
</template>
