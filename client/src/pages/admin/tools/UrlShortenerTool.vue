<script setup lang="ts">
import { onMounted, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useClipboard } from "@/composables/useClipboard";
import { useNotify } from "@/composables/useNotify";
import type { UrlItem } from "@/types";

const urls = ref<UrlItem[]>([]);
const newUrl = ref("");
const newTitle = ref("");
const loading = ref(false);
const { toast } = useNotify();
const { copy } = useClipboard();

async function loadUrls(): Promise<void> {
  try {
    const { data } = await api.get<UrlItem[]>("/tools/url-shortener");
    urls.value = data;
  } catch (err) {
    console.error(err);
    toast("Failed to load URLs", "error");
  }
}

async function createUrl(): Promise<void> {
  if (!newUrl.value.trim()) return;
  loading.value = true;
  try {
    await api.post("/tools/url-shortener", {
      original_url: newUrl.value,
      title: newTitle.value || null,
    });
    newUrl.value = "";
    newTitle.value = "";
    toast("URL created", "success");
    await loadUrls();
  } catch (err) {
    console.error(err);
    toast("Failed to create URL", "error");
  } finally {
    loading.value = false;
  }
}

async function deleteUrl(id: number): Promise<void> {
  try {
    await api.delete(`/tools/url-shortener/${id}`);
    toast("URL deleted", "success");
    await loadUrls();
  } catch (err) {
    console.error(err);
    toast("Failed to delete URL", "error");
  }
}

function getShortUrl(code: string): string {
  return `${window.location.origin}/s/${code}`;
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
      <BaseCard v-for="url in urls" :key="url.id" hoverable>
        <div class="flex justify-between items-start">
          <div class="flex-1 min-w-0">
            <div class="text-surface-light font-bold text-sm truncate">
              {{ url.title || url.original_url }}
            </div>
            <div class="text-xs text-surface-mid truncate mt-1">
              {{ url.original_url }}
            </div>
            <div class="flex items-center gap-3 mt-2">
              <code class="text-xs text-accent-blue">{{ getShortUrl(url.code) }}</code>
              <span class="text-xs text-surface-mid">{{ url.clicks }} clicks</span>
            </div>
          </div>
          <div class="flex gap-2 ml-4">
            <BaseButton variant="ghost" size="sm" @click="copy(getShortUrl(url.code))">
              Copy
            </BaseButton>
            <BaseButton variant="ghost" size="sm" @click="deleteUrl(url.id)"> Delete </BaseButton>
          </div>
        </div>
      </BaseCard>

      <p v-if="urls.length === 0" class="text-surface-mid text-sm text-center py-8">
        No shortened URLs yet. Create one above.
      </p>
    </div>
  </AdminPageLayout>
</template>
