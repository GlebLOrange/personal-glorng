<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { usePermissions } from "@/composables/usePermissions";
import { useQrLibrary, type QrErrorLevel, type QrStoredItem } from "@/composables/useQrLibrary";

interface QrGenerateResponse {
  content_preview: string;
  label: string | null;
  error_level: QrErrorLevel;
  svg: string;
}

const route = useRoute();
const content = ref("");
const label = ref("");
const errorLevel = ref<QrErrorLevel>("M");
const generated = ref<QrGenerateResponse | null>(null);
const previewUrl = ref("");
const editingId = ref<number | null>(null);

const { can } = usePermissions();
const canReadLibrary = computed(() => can("qr-generator", "read"));
const canWriteLibrary = computed(() => can("qr-generator", "write"));
const {
  loadOne,
  loadList,
  items,
  page,
  total,
  totalPages,
  loading: listLoading,
  hasNextPage,
  hasPreviousPage,
  goToPage,
} = useQrLibrary();

const { loading: creating, run: runCreate } = useApiAction();
const { loading: savingLibrary, run: runSaveLibrary } = useApiAction();
const loadingSaved = ref(false);

const canCreate = computed(() => Boolean(content.value.trim()) && !creating.value);
const canSaveLibrary = computed(
  () => canWriteLibrary.value && Boolean(content.value.trim()) && !savingLibrary.value,
);

function payloadBody(): {
  content: string;
  label: string | null;
  error_level: QrErrorLevel;
} {
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
  if (svg) {
    generated.value = {
      content_preview: item.content_preview,
      label: item.label,
      error_level: item.error_level,
      svg,
    };
  }
}

function setPreviewFromSvg(svg: string): void {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
  previewUrl.value = URL.createObjectURL(new Blob([svg], { type: "image/svg+xml" }));
}

watch(
  () => generated.value?.svg,
  (svg) => {
    if (svg) setPreviewFromSvg(svg);
    else if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value);
      previewUrl.value = "";
    }
  },
);

onBeforeUnmount(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
});

async function loadSavedFromQuery(): Promise<void> {
  const raw = route.query.saved;
  const id = typeof raw === "string" ? Number.parseInt(raw, 10) : Number.NaN;
  if (!Number.isFinite(id) || id < 1 || !canReadLibrary.value) return;

  loadingSaved.value = true;
  const item = await loadOne(id);
  loadingSaved.value = false;
  if (!item) return;

  let svg: string | null = item.svg ?? null;
  if (!svg) {
    const svgResp = await api.get<string>(item.svg_url, { responseType: "text" });
    svg = svgResp.data;
  }
  applyStored(item, svg);
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

async function selectSaved(item: QrStoredItem): Promise<void> {
  loadingSaved.value = true;
  const full = await loadOne(item.id);
  loadingSaved.value = false;
  if (!full) return;
  let svg: string | null = full.svg ?? null;
  if (!svg) {
    const svgResp = await api.get<string>(full.svg_url, { responseType: "text" });
    svg = svgResp.data;
  }
  applyStored(full, svg);
}

function downloadSvg(): void {
  const svg = generated.value?.svg;
  if (!svg) return;
  const url = URL.createObjectURL(new Blob([svg], { type: "image/svg+xml" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "qr-code.svg";
  anchor.click();
  URL.revokeObjectURL(url);
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
          <label class="block text-sm text-surface-mid">
            payload
            <textarea
              v-model="content"
              rows="4"
              maxlength="2000"
              placeholder="URL, text, Wi‑Fi string, etc."
              class="mt-1 w-full resize-y rounded-md border border-surface-border bg-surface-base px-3 py-2 text-sm text-surface-high focus:border-accent focus:outline-none"
            />
          </label>
          <div class="flex flex-wrap gap-3">
            <BaseInput
              v-model="label"
              label="label (optional)"
              placeholder="My link"
              class="min-w-0 flex-1"
              maxlength="120"
            />
            <label class="block text-sm text-surface-mid">
              error correction
              <select
                v-model="errorLevel"
                class="mt-1 block w-full rounded-md border border-surface-border bg-surface-base px-3 py-2 text-sm"
              >
                <option value="L">L (~7%)</option>
                <option value="M">M (~15%)</option>
                <option value="Q">Q (~25%)</option>
                <option value="H">H (~30%)</option>
              </select>
            </label>
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
                  : editingId
                    ? "update saved qr"
                    : "save to library"
              }}
            </BaseButton>
          </div>
          <p v-if="loadingSaved" class="text-xs text-surface-mid">Loading saved code…</p>
        </form>
      </Card>

      <Card variant="ghost" class="flex min-h-[280px] flex-col items-center justify-center gap-3 p-4">
        <img
          v-if="previewUrl"
          :src="previewUrl"
          :alt="previewAlt"
          class="max-h-64 max-w-full rounded-md bg-white p-2"
        />
        <p v-else class="text-center text-sm text-surface-mid">
          Generate a code to preview it here.
        </p>
        <button
          v-if="generated?.svg"
          type="button"
          class="text-sm text-accent hover:underline"
          @click="downloadSvg"
        >
          download svg
        </button>
      </Card>
    </div>

    <section v-if="canReadLibrary" class="mt-8 min-w-0">
      <h2 class="mb-3 text-sm font-medium text-surface-mid">your saved qr codes</h2>
      <AdminListSkeleton v-if="listLoading && items.length === 0" />
      <EmptyState
        v-else-if="!listLoading && items.length === 0"
        message="No saved QR codes yet. Generate one and save it."
      />
      <ul v-else class="divide-y divide-surface-border rounded-md border border-surface-border">
        <li v-for="item in items" :key="item.id">
          <button
            type="button"
            class="flex w-full min-w-0 items-center gap-3 px-3 py-3 text-left hover:bg-surface-raised/60"
            @click="selectSaved(item)"
          >
            <img
              :src="item.svg_url"
              alt=""
              class="size-12 shrink-0 rounded bg-white p-1"
              loading="lazy"
            />
            <span class="min-w-0 flex-1">
              <span class="block truncate text-sm text-surface-high">
                {{ item.label || item.content_preview }}
              </span>
              <span v-if="item.label" class="block truncate text-xs text-surface-mid">
                {{ item.content_preview }}
              </span>
            </span>
            <span class="shrink-0 text-xs text-surface-mid">{{ item.error_level }}</span>
          </button>
        </li>
      </ul>
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
