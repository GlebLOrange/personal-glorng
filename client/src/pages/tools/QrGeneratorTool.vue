<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import type { PaginatedList } from "@/types";

type QrErrorLevel = "L" | "M" | "Q" | "H";

interface QrCodeItem {
  id: number;
  content_preview: string;
  label: string | null;
  error_level: QrErrorLevel;
  svg_url: string;
  created_at: string;
}

const content = ref("");
const label = ref("");
const errorLevel = ref<QrErrorLevel>("M");
const active = ref<QrCodeItem | null>(null);
const items = ref<QrCodeItem[]>([]);
const page = ref(1);
const total = ref(0);
const totalPages = ref(0);

const { loading: creating, run: runCreate } = useApiAction();
const { loading: listLoading, run: runList } = useApiAction();

const canCreate = computed(() => Boolean(content.value.trim()) && !creating.value);
const hasNextPage = computed(() => page.value < totalPages.value);
const hasPreviousPage = computed(() => page.value > 1);
const previewSrc = computed(() => active.value?.svg_url ?? "");

async function loadList(): Promise<void> {
  const data = await runList(
    () =>
      api.get<PaginatedList<QrCodeItem>>("/tools/qr-generator", {
        params: { page: page.value, per_page: ADMIN_LIST_PAGE_SIZE },
      }),
    { errorFallback: "Failed to load QR codes" },
  );
  if (data) {
    items.value = data.data.items;
    total.value = data.data.total;
    totalPages.value = data.data.pages;
  }
}

function goToPage(nextPage: number): void {
  if (nextPage < 1) return;
  if (totalPages.value > 0 && nextPage > totalPages.value) return;
  page.value = nextPage;
  void loadList();
}

async function createQr(): Promise<void> {
  if (!content.value.trim()) return;
  const result = await runCreate(
    () =>
      api.post<QrCodeItem>("/tools/qr-generator", {
        content: content.value.trim(),
        label: label.value.trim() || null,
        error_level: errorLevel.value,
      }),
    { successMessage: "QR code created", errorFallback: "Failed to create QR code" },
  );
  if (result) {
    active.value = result.data;
    page.value = 1;
    await loadList();
  }
}

function selectItem(item: QrCodeItem): void {
  active.value = item;
}

onMounted(loadList);
</script>

<template>
  <PageShell
    title="qr generator"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'qr generator' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
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
          <BaseButton variant="primary" type="submit" :disabled="!canCreate">
            {{ creating ? "generating…" : "generate qr" }}
          </BaseButton>
        </form>
      </Card>

      <Card variant="ghost" class="flex min-h-[280px] flex-col items-center justify-center gap-3 p-4">
        <img
          v-if="previewSrc"
          :src="previewSrc"
          :alt="active?.label || active?.content_preview || 'QR code preview'"
          class="max-h-64 max-w-full rounded-md bg-white p-2"
        />
        <p v-else class="text-center text-sm text-surface-mid">
          Generate a code or pick one from the list.
        </p>
        <a
          v-if="previewSrc"
          :href="previewSrc"
          download
          class="text-sm text-accent hover:underline"
        >
          download svg
        </a>
      </Card>
    </div>

    <section class="mt-8 min-w-0">
      <h2 class="mb-3 text-sm font-medium text-surface-mid">recent qr codes</h2>
      <AdminListSkeleton v-if="listLoading && items.length === 0" />
      <EmptyState v-else-if="!listLoading && items.length === 0" message="No QR codes yet." />
      <ul v-else class="divide-y divide-surface-border rounded-md border border-surface-border">
        <li v-for="item in items" :key="item.id">
          <button
            type="button"
            class="flex w-full min-w-0 items-center gap-3 px-3 py-3 text-left hover:bg-surface-raised/60"
            @click="selectItem(item)"
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
        aria-label="QR codes pagination"
        @first="goToPage(1)"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
        @last="goToPage(totalPages)"
      />
    </section>
  </PageShell>
</template>
