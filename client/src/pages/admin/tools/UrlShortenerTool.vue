<script setup lang="ts">
import { onMounted, ref } from "vue";

import ShareableListItem from "@/components/admin/ShareableListItem.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import type { UrlItem } from "@/types";
import { publicUrl } from "@/utils/publicLinks";

const urls = ref<UrlItem[]>([]);
const newUrl = ref("");
const newTitle = ref("");
const { copy } = useClipboard();
const { run: runList } = useApiAction();
const { loading, run: runCreate } = useApiAction();
const { run: runDelete } = useApiAction();

async function loadUrls(): Promise<void> {
  const data = await runList(() => api.get<UrlItem[]>("/tools/url-shortener"), {
    errorFallback: "Failed to load URLs",
  });
  if (data) {
    urls.value = data.data;
  }
}

async function createUrl(): Promise<void> {
  if (!newUrl.value.trim()) return;
  const result = await runCreate(
    () =>
      api.post("/tools/url-shortener", {
        original_url: newUrl.value,
        title: newTitle.value || null,
      }),
    { successMessage: "URL created", errorFallback: "Failed to create URL" },
  );
  if (result) {
    newUrl.value = "";
    newTitle.value = "";
    await loadUrls();
  }
}

async function deleteUrl(id: number): Promise<void> {
  const result = await runDelete(() => api.delete(`/tools/url-shortener/${id}`), {
    successMessage: "URL deleted",
    errorFallback: "Failed to delete URL",
  });
  if (result) {
    await loadUrls();
  }
}

onMounted(loadUrls);
</script>

<template>
  <AdminPageLayout title="url-shortener">
    <form class="space-y-3 mb-10" @submit.prevent="createUrl">
      <BaseInput v-model="newUrl" placeholder="https://example.com/very-long-url..." label="URL" />
      <BaseInput v-model="newTitle" placeholder="Optional title" label="Title" />
      <BaseButton variant="primary" :disabled="loading">
        {{ loading ? "Creating..." : "Shorten" }}
      </BaseButton>
    </form>

    <div class="space-y-3">
      <ShareableListItem
        v-for="url in urls"
        :key="url.id"
        :title="url.title || url.original_url"
        :subtitle="url.original_url"
        :link="publicUrl('s', url.code)"
        :meta="`${url.clicks} clicks`"
        @copy="copy(publicUrl('s', url.code))"
        @delete="deleteUrl(url.id)"
      />

      <EmptyState v-if="urls.length === 0">No shortened URLs yet. Create one above.</EmptyState>
    </div>
  </AdminPageLayout>
</template>
