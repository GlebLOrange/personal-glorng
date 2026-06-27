<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import ShareableListItem from "@/components/admin/ShareableListItem.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useClipboard } from "@/composables/useClipboard";
import { usePermissions } from "@/composables/usePermissions";
import type { UrlItem } from "@/types";
import { publicUrl } from "@/utils/publicLinks";

const urls = ref<UrlItem[]>([]);
const newUrl = ref("");
const newTitle = ref("");
const lastCreatedLink = ref<string | null>(null);
const { copy } = useClipboard();
const { can } = usePermissions();
const canManage = computed(() => can("url-shortener", "read"));
const { run: runList } = useApiAction();
const { loading, run: runCreate } = useApiAction();
const { run: runDelete } = useApiAction();

async function loadUrls(): Promise<void> {
  if (!canManage.value) return;
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
    const code = result.data.code as string;
    lastCreatedLink.value = publicUrl("s", code);
    newUrl.value = "";
    newTitle.value = "";
    if (canManage.value) {
      await loadUrls();
    }
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
  <AdminPageLayout title="url-shortener" back-to="/tools">
    <form class="space-y-3 mb-10" @submit.prevent="createUrl">
      <BaseInput v-model="newUrl" placeholder="https://example.com/very-long-url..." label="URL" />
      <BaseInput v-model="newTitle" placeholder="Optional title" label="Title" />
      <BaseButton variant="primary" :disabled="loading">
        {{ loading ? "Creating..." : "Shorten" }}
      </BaseButton>
    </form>

    <div
      v-if="lastCreatedLink"
      class="mb-10 rounded-lg border border-surface-border bg-surface-card p-4"
    >
      <p class="text-sm text-surface-mid mb-2">Your short link</p>
      <div class="flex flex-wrap items-center gap-3">
        <a
          :href="lastCreatedLink"
          class="text-accent-blue text-sm break-all hover:underline"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ lastCreatedLink }}
        </a>
        <BaseButton variant="ghost" size="sm" @click="copy(lastCreatedLink)">Copy</BaseButton>
      </div>
    </div>

    <div v-if="canManage" class="space-y-3">
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
