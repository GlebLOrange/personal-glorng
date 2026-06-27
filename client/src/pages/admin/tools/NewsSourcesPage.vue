<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import type { NewsSource } from "@/types";
import { formatDate } from "@/utils/format";
import { normalizeHttpUrl, sourceFromMarkedUrl } from "@/utils/newsForms";

interface NewsSourceForm {
  name: string;
  feed_url: string;
  category: string;
  region: string;
  enabled: boolean;
}

interface MessageResponse {
  message: string;
}

const blankForm = (): NewsSourceForm => ({
  name: "",
  feed_url: "",
  category: "world",
  region: "global",
  enabled: true,
});

const sources = ref<NewsSource[]>([]);
const selectedSourceIds = ref<number[]>([]);
const form = ref<NewsSourceForm>(blankForm());
const editingId = ref<number | null>(null);
const loading = ref(true);
const loadError = ref(false);
const saving = ref(false);
const refreshing = ref(false);
const deletingId = ref<number | null>(null);
const lastAutoName = ref<string | null>(null);
const { toast } = useNotify();
const { can } = usePermissions();
const canWrite = computed(() => can("news-sources", "write"));
const formTitle = computed(() => (editingId.value ? "Edit source" : "Add source"));
const selectedSourceCount = computed(() => selectedSourceIds.value.length);
const refreshButtonText = computed(() => {
  if (refreshing.value) return "Queueing...";
  if (selectedSourceCount.value) return `Queue parser (${selectedSourceCount.value})`;
  return "Queue parser";
});

async function loadSources(): Promise<void> {
  loading.value = true;
  loadError.value = false;
  try {
    const { data } = await api.get<NewsSource[]>("/tools/news-sources");
    sources.value = data;
    selectedSourceIds.value = selectedSourceIds.value.filter((id) =>
      data.some((source) => source.id === id && source.enabled),
    );
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    loadError.value = true;
    toast("Failed to load news sources", "error");
  } finally {
    loading.value = false;
  }
}

function editSource(source: NewsSource): void {
  editingId.value = source.id;
  lastAutoName.value = null;
  form.value = {
    name: source.name,
    feed_url: source.feed_url,
    category: source.category,
    region: source.region,
    enabled: source.enabled,
  };
}

function resetForm(): void {
  editingId.value = null;
  lastAutoName.value = null;
  form.value = blankForm();
}

function payload(): Record<string, string | boolean | null> | null {
  const feedUrl = normalizeHttpUrl(form.value.feed_url);
  if (!feedUrl) {
    toast("Enter a valid http(s) feed URL", "error");
    return null;
  }
  return {
    name: form.value.name.trim(),
    feed_url: feedUrl,
    category: form.value.category.trim(),
    region: form.value.region.trim(),
    enabled: form.value.enabled,
  };
}

async function saveSource(): Promise<void> {
  if (!canWrite.value) return;
  saving.value = true;
  try {
    const requestPayload = payload();
    if (!requestPayload) return;
    if (editingId.value) {
      await api.put(`/tools/news-sources/${editingId.value}`, requestPayload);
      toast("News source updated", "success");
    } else {
      await api.post("/tools/news-sources", requestPayload);
      toast("News source created", "success");
    }
    resetForm();
    await loadSources();
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to save news source", "error");
  } finally {
    saving.value = false;
  }
}

async function refreshSources(): Promise<void> {
  if (!canWrite.value) return;
  refreshing.value = true;
  try {
    const { data } = await api.post<MessageResponse>("/tools/news-sources/refresh", {
      source_ids: selectedSourceIds.value.length ? selectedSourceIds.value : null,
    });
    toast(data.message, "success");
    await loadSources();
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to queue news parser", "error");
  } finally {
    refreshing.value = false;
  }
}

async function deleteSource(source: NewsSource): Promise<void> {
  if (!canWrite.value) return;
  if (!window.confirm(`Delete ${source.name}?`)) return;
  deletingId.value = source.id;
  try {
    await api.delete(`/tools/news-sources/${source.id}`);
    sources.value = sources.value.filter((item) => item.id !== source.id);
    if (editingId.value === source.id) resetForm();
    toast("News source deleted", "success");
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to delete news source", "error");
  } finally {
    deletingId.value = null;
  }
}

watch(
  () => form.value.feed_url,
  (feedUrl) => {
    if (editingId.value) return;
    const source = sourceFromMarkedUrl(feedUrl);
    if (!source) return;
    const currentName = form.value.name.trim();
    if (currentName && currentName !== lastAutoName.value) return;
    form.value.name = source;
    lastAutoName.value = source;
  },
);

onMounted(loadSources);
</script>

<template>
  <AdminPageLayout title="news sources" max-width="xl">
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_22rem]">
      <div class="space-y-4">
        <div class="flex justify-end">
          <BaseButton
            v-if="canWrite"
            variant="ghost"
            :disabled="refreshing"
            @click="refreshSources"
          >
            {{ refreshButtonText }}
          </BaseButton>
        </div>

        <div v-if="loading" class="space-y-3" aria-busy="true" aria-label="Loading sources">
          <div
            v-for="i in 5"
            :key="i"
            class="h-28 animate-pulse rounded-lg border border-surface-border bg-surface-card"
          />
        </div>

        <BaseCard v-else-if="loadError" role="alert">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p class="text-sm text-accent-golden">News sources could not be loaded.</p>
            <BaseButton variant="ghost" size="sm" @click="loadSources">Retry</BaseButton>
          </div>
        </BaseCard>

        <BaseCard v-else-if="sources.length === 0">
          <p class="text-sm text-surface-mid">No news sources yet.</p>
        </BaseCard>

        <template v-else>
          <BaseCard v-for="source in sources" :key="source.id">
            <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div class="min-w-0 flex-1">
                <div class="mb-2 flex flex-wrap items-center gap-2">
                  <input
                    v-if="canWrite"
                    v-model="selectedSourceIds"
                    type="checkbox"
                    class="size-4 accent-accent-blue"
                    :value="source.id"
                    :disabled="refreshing || !source.enabled"
                    :aria-label="`Select ${source.name} for parser refresh`"
                  />
                  <h2 class="truncate text-base font-bold text-surface-light">{{ source.name }}</h2>
                  <span
                    class="rounded px-2 py-0.5 text-[10px]"
                    :class="
                      source.enabled
                        ? 'bg-accent-blue/20 text-accent-blue'
                        : 'bg-surface-border text-surface-mid'
                    "
                  >
                    {{ source.enabled ? "enabled" : "disabled" }}
                  </span>
                </div>
                <p class="break-all text-xs text-surface-mid">{{ source.feed_url }}</p>
                <p class="mt-2 text-xs text-surface-muted">
                  {{ source.category }} · {{ source.region }}
                  <span v-if="source.last_fetched_at">
                    · fetched {{ formatDate(source.last_fetched_at) }}
                  </span>
                </p>
                <p v-if="source.last_error" class="mt-2 text-xs text-accent-golden">
                  Last error: {{ source.last_error }}
                </p>
              </div>
              <div class="flex shrink-0 gap-2">
                <BaseButton v-if="canWrite" variant="ghost" size="sm" @click="editSource(source)">
                  Edit
                </BaseButton>
                <BaseButton
                  v-if="canWrite"
                  variant="ghost"
                  size="sm"
                  :disabled="deletingId === source.id"
                  @click="deleteSource(source)"
                >
                  Delete
                </BaseButton>
              </div>
            </div>
          </BaseCard>
        </template>
      </div>

      <BaseCard v-if="canWrite">
        <h2 class="mb-4 text-lg font-bold text-surface-light">{{ formTitle }}</h2>
        <form class="space-y-4" @submit.prevent="saveSource">
          <BaseInput v-model="form.name" label="Name" required />
          <BaseInput v-model="form.feed_url" label="Feed URL" type="url" required />
          <BaseInput v-model="form.category" label="Category" required />
          <BaseInput v-model="form.region" label="Region" required />
          <label class="flex items-center gap-2 text-sm text-surface-mid">
            <input v-model="form.enabled" type="checkbox" class="size-4 accent-accent-blue" />
            Enabled
          </label>
          <div class="flex gap-2">
            <BaseButton type="submit" variant="primary" :disabled="saving">
              {{ saving ? "Saving..." : "Save" }}
            </BaseButton>
            <BaseButton type="button" variant="ghost" @click="resetForm">Cancel</BaseButton>
          </div>
        </form>
      </BaseCard>
    </div>
  </AdminPageLayout>
</template>
