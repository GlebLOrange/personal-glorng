<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import UrlShortenerListItem from "@/components/admin/UrlShortenerListItem.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import { usePermissions } from "@/composables/usePermissions";
import type { PaginatedList, UrlItem } from "@/types";
import { ensureHttpsUrl } from "@/utils/ensureHttpsUrl";
import { publicUrl } from "@/utils/publicLinks";

const urls = ref<UrlItem[]>([]);
const page = ref(1);
const total = ref(0);
const totalPages = ref(0);
const newUrl = ref("");
const newTitle = ref("");
const savingId = ref<number | null>(null);
const deletingId = ref<number | null>(null);
const { copy } = useClipboard();
const { can } = usePermissions();
const canManage = computed(() => can("url-shortener", "read"));
const canWrite = computed(() => can("url-shortener", "write"));
const { loading: listLoading, run: runList } = useApiAction();
const { loading, run: runCreate } = useApiAction();
const { run: runUpdate } = useApiAction();
const { run: runDelete } = useApiAction();

const hasNextPage = computed(() => page.value < totalPages.value);
const hasPreviousPage = computed(() => page.value > 1);
const canShorten = computed(() => Boolean(newUrl.value.trim()) && !loading.value);

async function loadUrls(): Promise<void> {
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
  if (!newUrl.value.trim()) return;
  const result = await runCreate(
    () =>
      api.post("/tools/url-shortener", {
        original_url: ensureHttpsUrl(newUrl.value),
        title: newTitle.value || null,
      }),
    { successMessage: "URL created", errorFallback: "Failed to create URL" },
  );
  if (result) {
    newUrl.value = "";
    newTitle.value = "";
    if (canManage.value) {
      page.value = 1;
      await loadUrls();
    }
  }
}

async function updateUrl(id: number, title: string | null): Promise<void> {
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

onMounted(loadUrls);
</script>

<template>
  <PageShell
    title="url shortener"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'url shortener' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
    <form class="mb-6 space-y-3" @submit.prevent="createUrl">
      <div class="mb-3 flex w-full min-w-0 items-center justify-end">
        <ToolbarPillButton family="2xx" type="submit" :disabled="!canShorten">
          {{ loading ? "creating…" : "shorten" }}
        </ToolbarPillButton>
      </div>
      <BaseInput
        v-model="newUrl"
        class="min-w-0 w-full"
        placeholder="url (example.com or https://…)"
        aria-label="url (example.com or https://…)"
      />
      <BaseInput v-model="newTitle" placeholder="title (optional)" aria-label="title" />
    </form>

    <div v-if="canManage" class="min-w-0">
      <AdminListSkeleton v-if="listLoading" label="loading shortened URLs" />

      <template v-else>
        <div v-if="urls.length > 0" class="min-w-0 space-y-2">
          <UrlShortenerListItem
            v-for="url in urls"
            :key="url.id"
            :url="url"
            :can-write="canWrite"
            :saving="savingId === url.id"
            :deleting="deletingId === url.id"
            @copy="copy(publicUrl('s', url.code))"
            @save="updateUrl(url.id, $event)"
            @delete="deleteUrl(url.id)"
          />
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
