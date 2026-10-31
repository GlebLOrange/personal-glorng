<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import UrlShortenerListItem from "@/components/admin/UrlShortenerListItem.vue";
import { ADMIN_TH_CLASS } from "@/constants/adminDataTable";
import PageShell from "@/components/layout/PageShell.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import { useLocalStorage } from "@/composables/useLocalStorage";
import { usePermissions } from "@/composables/usePermissions";
import type { PaginatedList, UrlItem } from "@/types";
import {
  createGuestShortUrl,
  deleteGuestShortUrl,
  GUEST_URL_SHORTENER_KEY,
  guestUrlLimitMessage,
  sanitizeGuestShortUrls,
  updateGuestShortUrlTitle,
} from "@/utils/guestUrlShortener";
import { ensureHttpsUrl } from "@/utils/safeUrl";
import { publicUrl } from "@/utils/publicLinks";

const urls = ref<UrlItem[]>([]);
const page = ref(1);
const total = ref(0);
const totalPages = ref(0);
const newUrl = ref("");
const newTitle = ref("");
const formError = ref("");
const savingId = ref<number | null>(null);
const deletingId = ref<number | null>(null);
const { copy } = useClipboard();
const { can } = usePermissions();
const canManage = computed(() => can("url-shortener", "read"));
const canWriteServer = computed(() => can("url-shortener", "write"));
/** Local demo store when the account library is unavailable. */
const isLocalMode = computed(() => !canManage.value);
const canWrite = computed(() => isLocalMode.value || canWriteServer.value);
const { loading: listLoading, run: runList } = useApiAction();
const { loading, lastError, run: runCreate } = useApiAction();
const { run: runUpdate } = useApiAction();
const { run: runDelete } = useApiAction();

const guestStored = useLocalStorage<unknown>(GUEST_URL_SHORTENER_KEY, []);
const guestUrls = ref<UrlItem[]>(sanitizeGuestShortUrls(guestStored.value));

watch(
  guestUrls,
  (next) => {
    guestStored.value = next;
  },
  { deep: true },
);

watch(isLocalMode, (local) => {
  if (local) {
    guestUrls.value = sanitizeGuestShortUrls(guestStored.value);
    page.value = 1;
    syncLocalPage();
  } else {
    void loadUrls();
  }
});

const hasNextPage = computed(() => page.value < totalPages.value);
const hasPreviousPage = computed(() => page.value > 1);
const canShorten = computed(() => Boolean(newUrl.value.trim()) && !loading.value);

const URL_FORMAT_HINT = "enter a full URL like https://example.com";

function isShortenableUrl(raw: string): boolean {
  try {
    const parsed = new URL(ensureHttpsUrl(raw));
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

const urlTone = computed<"error" | undefined>(() => {
  if (!formError.value && !newUrl.value.trim()) return undefined;
  if (formError.value) return "error";
  if (newUrl.value.trim() && !isShortenableUrl(newUrl.value)) return "error";
  return undefined;
});

const urlError = computed(() => {
  if (formError.value) return formError.value;
  if (newUrl.value.trim() && !isShortenableUrl(newUrl.value)) return URL_FORMAT_HINT;
  return undefined;
});

function syncLocalPage(): void {
  const all = guestUrls.value;
  total.value = all.length;
  totalPages.value = Math.max(1, Math.ceil(all.length / ADMIN_LIST_PAGE_SIZE) || 1);
  if (all.length === 0) {
    totalPages.value = 0;
    urls.value = [];
    return;
  }
  if (page.value > totalPages.value) {
    page.value = totalPages.value;
  }
  const start = (page.value - 1) * ADMIN_LIST_PAGE_SIZE;
  urls.value = all.slice(start, start + ADMIN_LIST_PAGE_SIZE);
}

async function loadUrls(): Promise<void> {
  if (isLocalMode.value) {
    syncLocalPage();
    return;
  }
  if (!canManage.value) return;
  const data = await runList(
    () =>
      api.get<PaginatedList<UrlItem>>("/tools/url-shortener", {
        params: { page: page.value, per_page: ADMIN_LIST_PAGE_SIZE },
      }),
    {
      errorFallback: "Failed to load URLs",
    },
  );
  if (data) {
    urls.value = data.data.items;
    total.value = data.data.total;
    totalPages.value = data.data.pages;
  }
}

function goToPage(nextPage: number): void {
  if (nextPage < 1) return;
  if (totalPages.value > 0 && nextPage > totalPages.value) return;
  page.value = nextPage;
  void loadUrls();
}

async function createUrl(): Promise<void> {
  const trimmed = newUrl.value.trim();
  if (!trimmed) return;
  formError.value = "";
  if (!isShortenableUrl(trimmed)) {
    formError.value = URL_FORMAT_HINT;
    return;
  }

  if (isLocalMode.value) {
    const result = createGuestShortUrl(guestUrls.value, trimmed, newTitle.value || null);
    if (!result.ok) {
      formError.value = result.error;
      return;
    }
    guestUrls.value = result.next;
    newUrl.value = "";
    newTitle.value = "";
    formError.value = "";
    page.value = 1;
    syncLocalPage();
    return;
  }

  const result = await runCreate(
    () =>
      api.post("/tools/url-shortener", {
        original_url: ensureHttpsUrl(trimmed),
        title: newTitle.value || null,
      }),
    { successMessage: "URL created", errorFallback: "Failed to create URL" },
  );
  if (result) {
    newUrl.value = "";
    newTitle.value = "";
    formError.value = "";
    if (canManage.value) {
      page.value = 1;
      await loadUrls();
    }
    return;
  }
  // Keep a durable inline error — toast alone is easy to miss after submit.
  formError.value = lastError.value ?? "Failed to create URL";
}

async function updateUrl(id: number, title: string | null): Promise<void> {
  if (isLocalMode.value) {
    savingId.value = id;
    guestUrls.value = updateGuestShortUrlTitle(guestUrls.value, id, title);
    savingId.value = null;
    syncLocalPage();
    return;
  }
  savingId.value = id;
  const result = await runUpdate(
    () => api.patch<UrlItem>(`/tools/url-shortener/${id}`, { title }),
    { successMessage: "Title updated", errorFallback: "Failed to update title" },
  );
  savingId.value = null;
  if (result) {
    const index = urls.value.findIndex((url) => url.id === id);
    if (index !== -1) {
      urls.value[index] = result.data;
    }
  }
}

async function deleteUrl(id: number): Promise<void> {
  if (isLocalMode.value) {
    deletingId.value = id;
    guestUrls.value = deleteGuestShortUrl(guestUrls.value, id);
    deletingId.value = null;
    syncLocalPage();
    return;
  }
  deletingId.value = id;
  const result = await runDelete(() => api.delete(`/tools/url-shortener/${id}`), {
    successMessage: "URL deleted",
    errorFallback: "Failed to delete URL",
  });
  deletingId.value = null;
  if (result) {
    await loadUrls();
  }
}

function onCopy(url: UrlItem): void {
  if (isLocalMode.value) {
    void copy(url.original_url);
    return;
  }
  void copy(publicUrl("s", url.code));
}

onMounted(() => {
  if (isLocalMode.value) {
    guestUrls.value = sanitizeGuestShortUrls(guestStored.value);
  }
  void loadUrls();
});
</script>

<template>
  <PageShell
    title="url shortener"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'url shortener' }]"
    back-to="/tools"
    max-width="5xl"
    body-width="column"
  >
    <div class="page-tool-actions">
      <form class="flex w-full min-w-0 flex-col gap-2" @submit.prevent="createUrl">
        <BaseInput
          v-model="newUrl"
          class="w-full min-w-0"
          compact
          label="url"
          tip="example.com or https://…"
          :tone="urlTone"
          :error="urlError"
          @update:model-value="formError = ''"
        />
        <div class="flex w-full min-w-0 flex-wrap items-center gap-2">
          <BaseInput
            v-model="newTitle"
            class="min-w-0 flex-1"
            compact
            label="title"
            tip="optional"
          />
          <ToolbarPillButton
            action="create"
            type="submit"
            class="w-auto shrink-0"
            :disabled="!canShorten"
          >
            {{ loading ? "creating…" : "shorten" }}
          </ToolbarPillButton>
        </div>
      </form>
    </div>

    <p
      v-if="isLocalMode && guestUrls.length > 0"
      class="mb-2 w-full self-stretch text-xs text-surface-mid"
      role="status"
    >
      {{ guestUrlLimitMessage(guestUrls.length) }}
    </p>

    <div class="w-full min-w-0 self-stretch">
      <AdminListSkeleton v-if="listLoading && !isLocalMode" label="loading shortened URLs" />

      <template v-else>
        <div v-if="urls.length > 0" class="min-w-0">
          <AdminDataTable table-label="shortened URLs">
            <template #header>
              <th :class="ADMIN_TH_CLASS" scope="col">title</th>
              <th :class="ADMIN_TH_CLASS" scope="col">short link</th>
              <th :class="ADMIN_TH_CLASS" scope="col">original URL</th>
              <th :class="[ADMIN_TH_CLASS, 'w-px text-right']" scope="col">actions</th>
            </template>
            <UrlShortenerListItem
              v-for="url in urls"
              :key="url.id"
              :url="url"
              :can-write="canWrite"
              :local-row="isLocalMode"
              :saving="savingId === url.id"
              :deleting="deletingId === url.id"
              @copy="onCopy(url)"
              @save="updateUrl(url.id, $event)"
              @delete="deleteUrl(url.id)"
            />
          </AdminDataTable>
        </div>

        <EmptyState v-else>no shortened URLs yet. create one above.</EmptyState>

        <AdminListFooter
          v-if="urls.length > 0"
          :total="total"
          :page="page"
          :total-pages="totalPages"
          :has-next-page="hasNextPage"
          :has-previous-page="hasPreviousPage"
          :loading="listLoading"
          item-label="URLs"
          aria-label="short URLs pagination"
          @first="goToPage(1)"
          @prev="goToPage(page - 1)"
          @next="goToPage(page + 1)"
          @last="goToPage(totalPages)"
        />
      </template>
    </div>
  </PageShell>
</template>
