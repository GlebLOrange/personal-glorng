<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import { getApiErrorMessage } from "@/types/api";
import type { NewsAdminArticle, NewsSource } from "@/types";
import { formatDate } from "@/utils/format";
import { normalizeHttpUrl, sourceFromNewsLink, sourceKey, titleFromNewsLink } from "@/utils/newsForms";

interface NewsArticleForm {
  title: string;
  link: string;
  source: string;
  status: string;
  category: string;
  region: string;
  summary: string;
  published_at: string;
  enabled: boolean;
}

const NEWS_STATUSES = ["draft", "moderating", "published", "archived"] as const;
type NewsArticleStatus = (typeof NEWS_STATUSES)[number];
type NewsSort =
  | "published_at:desc"
  | "published_at:asc"
  | "created_at:desc"
  | "created_at:asc"
  | "updated_at:desc"
  | "updated_at:asc";

function datetimeInputValue(iso?: string): string {
  const date = iso ? new Date(iso) : new Date();
  const offset = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

const blankForm = (): NewsArticleForm => ({
  title: "",
  link: "",
  source: "gLOrng",
  status: "moderating",
  category: "world",
  region: "global",
  summary: "",
  published_at: datetimeInputValue(),
  enabled: true,
});

const articles = ref<NewsAdminArticle[]>([]);
const sources = ref<NewsSource[]>([]);
const form = ref<NewsArticleForm>(blankForm());
const selectedStatuses = ref<NewsArticleStatus[]>([...NEWS_STATUSES]);
const selectedSort = ref<NewsSort>("published_at:desc");
const editingId = ref<number | null>(null);
const drawerOpen = ref(false);
const loading = ref(true);
const loadError = ref(false);
const saving = ref(false);
const deletingId = ref<number | null>(null);
const lastAutoTitle = ref<string | null>(null);
const lastAutoSource = ref<string | null>(null);
const { toast } = useNotify();
const { can } = usePermissions();
const canWrite = computed(() => can("news", "write"));
const formTitle = computed(() => (editingId.value ? "Edit news" : "Add news"));
const isDefaultStatuses = computed(() => selectedStatuses.value.length === NEWS_STATUSES.length);
const hasAdminFilters = computed(
  () => !isDefaultStatuses.value || selectedSort.value !== "published_at:desc",
);
const sourceOptionNames = computed(() => {
  const names: string[] = [];
  const seen = new Set<string>();
  for (const source of sources.value) {
    const key = sourceKey(source.name);
    if (seen.has(key)) continue;
    seen.add(key);
    names.push(source.name);
  }
  const currentSource = form.value.source.trim();
  const currentKey = sourceKey(currentSource);
  if (currentSource && currentSource !== "gLOrng" && !seen.has(currentKey)) {
    names.unshift(currentSource);
  }
  return names;
});

async function loadArticles(): Promise<void> {
  loading.value = true;
  loadError.value = false;
  try {
    const params = new URLSearchParams();
    const [sortBy, sortOrder] = selectedSort.value.split(":");
    if (!isDefaultStatuses.value) {
      for (const status of selectedStatuses.value) params.append("status", status);
    }
    params.set("sort_by", sortBy);
    params.set("sort_order", sortOrder);
    const { data } = await api.get<NewsAdminArticle[]>(`/tools/news?${params.toString()}`);
    articles.value = data;
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    loadError.value = true;
    toast("Failed to load news", "error");
  } finally {
    loading.value = false;
  }
}

function clearAdminFilters(): void {
  selectedStatuses.value = [...NEWS_STATUSES];
  selectedSort.value = "published_at:desc";
}

async function loadSources(): Promise<void> {
  try {
    const { data } = await api.get<NewsSource[]>("/tools/news-sources");
    sources.value = data;
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to load news sources", "error");
  }
}

function editArticle(article: NewsAdminArticle): void {
  editingId.value = article.id;
  lastAutoTitle.value = null;
  lastAutoSource.value = null;
  form.value = {
    title: article.title,
    link: article.link,
    source: article.source,
    status: article.status,
    category: article.category,
    region: article.region,
    summary: article.summary ?? "",
    published_at: datetimeInputValue(article.published_at),
    enabled: article.enabled,
  };
  drawerOpen.value = true;
}

function openCreateDrawer(): void {
  // #region agent log
  fetch('http://127.0.0.1:7759/ingest/a59c5ce7-5b46-408d-8a93-dd9a50b51892',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'c5418e'},body:JSON.stringify({sessionId:'c5418e',runId:'initial',hypothesisId:'H1,H6',location:'client/src/pages/admin/tools/NewsAdminPage.vue:openCreateDrawer',message:'admin news create drawer opened',data:{canWrite:canWrite.value,articleCount:articles.value.length,sourceCount:sources.value.length},timestamp:Date.now()})}).catch(()=>{});
  // #endregion
  editingId.value = null;
  lastAutoTitle.value = null;
  lastAutoSource.value = null;
  form.value = blankForm();
  drawerOpen.value = true;
}

function closeDrawer(force = false): void {
  if (saving.value && !force) return;
  drawerOpen.value = false;
  editingId.value = null;
  form.value = blankForm();
}

function payload(): Record<string, string | boolean | null> | null {
  const normalizedLink = normalizeHttpUrl(form.value.link);
  if (!normalizedLink) {
    toast("Enter a valid http(s) news link", "error");
    return null;
  }
  const derivedTitle = titleFromNewsLink(form.value.link);
  const matchedSource = sourceFromNewsLink(form.value.link, sources.value);
  const selectedSource = form.value.source.trim();
  const publishedAt = new Date(form.value.published_at);
  if (Number.isNaN(publishedAt.getTime())) {
    toast("Enter a valid publish date", "error");
    return null;
  }
  return {
    title: form.value.title.trim() || derivedTitle || "",
    link: normalizedLink,
    source: selectedSource === "gLOrng" ? matchedSource || "gLOrng" : selectedSource || "gLOrng",
    status: form.value.status,
    category: form.value.category.trim(),
    region: form.value.region.trim(),
    summary: form.value.summary.trim() || null,
    published_at: publishedAt.toISOString(),
    enabled: form.value.enabled,
  };
}

function sourceOptionLabel(sourceName: string): string {
  const exists = sources.value.some((source) => sourceKey(source.name) === sourceKey(sourceName));
  return exists ? sourceName : `${sourceName} (new from URL)`;
}

watch([() => form.value.link, () => sources.value], ([link]) => {
  if (editingId.value) return;
  const title = titleFromNewsLink(link);
  if (title) {
    const currentTitle = form.value.title.trim();
    if (!currentTitle || currentTitle === lastAutoTitle.value) {
      form.value.title = title;
      lastAutoTitle.value = title;
    }
  }

  const source = sourceFromNewsLink(link, sources.value);
  if (!source) return;
  const currentSource = form.value.source.trim();
  if (currentSource && currentSource !== "gLOrng" && currentSource !== lastAutoSource.value) return;
  form.value.source = source;
  lastAutoSource.value = source;
});

watch(
  [selectedStatuses, selectedSort],
  async () => {
    await loadArticles();
  },
  { deep: true },
);

async function saveArticle(): Promise<void> {
  // #region agent log
  fetch('http://127.0.0.1:7759/ingest/a59c5ce7-5b46-408d-8a93-dd9a50b51892',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'c5418e'},body:JSON.stringify({sessionId:'c5418e',runId:'initial',hypothesisId:'H1,H6',location:'client/src/pages/admin/tools/NewsAdminPage.vue:saveArticle:before_guard',message:'admin news submit reached before permission guard',data:{canWrite:canWrite.value,editingId:editingId.value,linkLength:form.value.link.length,titleLength:form.value.title.length},timestamp:Date.now()})}).catch(()=>{});
  // #endregion
  if (!canWrite.value) return;
  saving.value = true;
  try {
    // #region agent log
    fetch('http://127.0.0.1:7759/ingest/a59c5ce7-5b46-408d-8a93-dd9a50b51892',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'c5418e'},body:JSON.stringify({sessionId:'c5418e',runId:'initial',hypothesisId:'H1,H2',location:'client/src/pages/admin/tools/NewsAdminPage.vue:saveArticle:start',message:'admin news save started',data:{canWrite:canWrite.value,editingId:editingId.value,linkLength:form.value.link.length,titleLength:form.value.title.length,status:form.value.status,source:form.value.source,category:form.value.category,region:form.value.region,publishedAt:form.value.published_at},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    const requestPayload = payload();
    if (!requestPayload) return;
    // #region agent log
    fetch('http://127.0.0.1:7759/ingest/a59c5ce7-5b46-408d-8a93-dd9a50b51892',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'c5418e'},body:JSON.stringify({sessionId:'c5418e',runId:'initial',hypothesisId:'H2,H3',location:'client/src/pages/admin/tools/NewsAdminPage.vue:saveArticle:payload',message:'admin news payload built',data:{editingId:editingId.value,link:requestPayload.link,titleLength:String(requestPayload.title ?? '').length,source:requestPayload.source,status:requestPayload.status,category:requestPayload.category,region:requestPayload.region,publishedAt:requestPayload.published_at,duplicateInLoadedArticles:articles.value.some((article) => article.link === requestPayload.link)},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    if (editingId.value) {
      await api.put(`/tools/news/${editingId.value}`, requestPayload);
      toast("News updated", "success");
    } else {
      if (articles.value.some((article) => article.link === requestPayload.link)) {
        toast("A news article with this link already exists", "error");
        return;
      }
      await api.post<NewsAdminArticle>("/tools/news", requestPayload);
      toast("News created", "success");
    }
    closeDrawer(true);
    await Promise.all([loadArticles(), loadSources()]);
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    // #region agent log
    fetch('http://127.0.0.1:7759/ingest/a59c5ce7-5b46-408d-8a93-dd9a50b51892',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'c5418e'},body:JSON.stringify({sessionId:'c5418e',runId:'initial',hypothesisId:'H3,H4,H5',location:'client/src/pages/admin/tools/NewsAdminPage.vue:saveArticle:catch',message:'admin news save failed in client',data:{status:err && typeof err === 'object' && 'response' in err ? (err as { response?: { status?: number; data?: unknown } }).response?.status : null,responseData:err && typeof err === 'object' && 'response' in err ? (err as { response?: { data?: unknown } }).response?.data : null,message:err instanceof Error ? err.message : String(err)},timestamp:Date.now()})}).catch(()=>{});
    // #endregion
    toast(getApiErrorMessage(err, "Failed to save news"), "error");
  } finally {
    saving.value = false;
  }
}

async function deleteArticle(article: NewsAdminArticle): Promise<void> {
  if (!canWrite.value) return;
  if (!window.confirm(`Delete ${article.title}?`)) return;
  deletingId.value = article.id;
  try {
    await api.delete(`/tools/news/${article.id}`);
    articles.value = articles.value.filter((item) => item.id !== article.id);
    if (editingId.value === article.id) closeDrawer();
    toast("News deleted", "success");
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to delete news", "error");
  } finally {
    deletingId.value = null;
  }
}

onMounted(() => {
  void loadSources();
  void loadArticles();
});
</script>

<template>
  <AdminPageLayout title="news" max-width="xl">
    <div class="space-y-4">
      <div class="flex justify-end">
        <BaseButton v-if="canWrite" variant="primary" @click="openCreateDrawer"
          >Add news</BaseButton
        >
      </div>

      <BaseCard>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-[1fr_auto] md:items-end">
          <fieldset>
            <legend class="mb-2 text-sm text-surface-mid">Statuses</legend>
            <div class="flex flex-wrap gap-3 text-sm text-surface-mid">
              <label v-for="status in NEWS_STATUSES" :key="status" class="flex items-center gap-2">
                <input
                  v-model="selectedStatuses"
                  type="checkbox"
                  class="size-4 accent-accent-blue"
                  :value="status"
                  :disabled="selectedStatuses.length === 1 && selectedStatuses.includes(status)"
                />
                {{ status }}
              </label>
            </div>
          </fieldset>
          <BaseSelect v-model="selectedSort" label="Sort">
            <option value="published_at:desc">Published newest</option>
            <option value="published_at:asc">Published oldest</option>
            <option value="created_at:desc">Created newest</option>
            <option value="created_at:asc">Created oldest</option>
            <option value="updated_at:desc">Updated newest</option>
            <option value="updated_at:asc">Updated oldest</option>
          </BaseSelect>
        </div>
        <div class="mt-3 flex justify-end">
          <BaseButton
            variant="ghost"
            size="sm"
            :disabled="!hasAdminFilters"
            @click="clearAdminFilters"
          >
            Clear filters
          </BaseButton>
        </div>
      </BaseCard>

      <div v-if="loading" class="space-y-3" aria-busy="true" aria-label="Loading news">
        <div
          v-for="i in 5"
          :key="i"
          class="h-32 animate-pulse rounded-lg border border-surface-border bg-surface-card"
        />
      </div>

      <BaseCard v-else-if="loadError" role="alert">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p class="text-sm text-accent-golden">News could not be loaded.</p>
          <BaseButton variant="ghost" size="sm" @click="loadArticles">Retry</BaseButton>
        </div>
      </BaseCard>

      <BaseCard v-else-if="articles.length === 0">
        <p class="text-sm text-surface-mid">
          {{ hasAdminFilters ? "No news match those filters." : "No curated news yet." }}
        </p>
      </BaseCard>

      <template v-else>
        <BaseCard v-for="article in articles" :key="article.id">
          <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div class="min-w-0 flex-1">
              <div class="mb-2 flex flex-wrap items-center gap-2">
                <h2 class="break-words text-base font-bold text-surface-light">
                  {{ article.title }}
                </h2>
                <span
                  class="rounded px-2 py-0.5 text-[10px]"
                  :class="
                    article.enabled
                      ? 'bg-accent-blue/20 text-accent-blue'
                      : 'bg-surface-border text-surface-mid'
                  "
                >
                  {{ article.enabled ? "enabled" : "disabled" }}
                </span>
                <span class="rounded bg-surface-border px-2 py-0.5 text-[10px] text-surface-mid">
                  {{ article.status }}
                </span>
                <span class="rounded bg-surface-border px-2 py-0.5 text-[10px] text-surface-mid">
                  {{ article.origin }}
                </span>
              </div>
              <p class="text-xs text-surface-mid">
                {{ article.source }} · {{ article.category }} · {{ article.region }} · Published
                {{ formatDate(article.published_at) }}
              </p>
              <p class="mt-1 text-xs text-surface-muted">
                Created {{ formatDate(article.created_at) }} · Updated
                {{ formatDate(article.updated_at) }}
              </p>
              <p v-if="article.summary" class="mt-2 text-sm text-surface-sage">
                {{ article.summary }}
              </p>
              <a
                :href="article.link"
                target="_blank"
                rel="noopener noreferrer"
                class="mt-2 inline-block max-w-full break-all text-xs text-accent-blue hover:underline"
              >
                {{ article.link }}
              </a>
            </div>
            <div class="flex shrink-0 gap-2">
              <BaseButton v-if="canWrite" variant="ghost" size="sm" @click="editArticle(article)">
                Edit
              </BaseButton>
              <BaseButton
                v-if="canWrite"
                variant="ghost"
                size="sm"
                :disabled="deletingId === article.id"
                @click="deleteArticle(article)"
              >
                Delete
              </BaseButton>
            </div>
          </div>
        </BaseCard>
      </template>
    </div>

    <BaseDrawer :open="drawerOpen" :title="formTitle" max-width="lg" @close="closeDrawer">
      <template #default>
        <form id="news-article-form" class="space-y-4" @submit.prevent="saveArticle">
          <BaseInput v-model="form.link" label="Link" type="url" required />
          <BaseInput v-model="form.title" label="Title" required />
          <BaseSelect v-model="form.source" label="Source">
            <option value="gLOrng">Auto-detect from URL</option>
            <option v-for="sourceName in sourceOptionNames" :key="sourceName" :value="sourceName">
              {{ sourceOptionLabel(sourceName) }}
            </option>
          </BaseSelect>
          <BaseSelect v-model="form.status" label="Status">
            <option value="draft">Draft</option>
            <option value="moderating">Moderating</option>
            <option value="published">Published</option>
            <option value="archived">Archived</option>
          </BaseSelect>
          <BaseInput v-model="form.category" label="Category" required />
          <BaseInput v-model="form.region" label="Region" required />
          <BaseInput
            v-model="form.published_at"
            label="Published at"
            type="datetime-local"
            required
          />
          <BaseTextarea v-model="form.summary" label="Summary" :rows="4" />
          <label class="flex items-center gap-2 text-sm text-surface-mid">
            <input v-model="form.enabled" type="checkbox" class="size-4 accent-accent-blue" />
            Enabled
          </label>
        </form>
      </template>

      <template #footer>
        <div class="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <BaseButton type="button" variant="ghost" :disabled="saving" @click="closeDrawer">
            Cancel
          </BaseButton>
          <BaseButton type="submit" form="news-article-form" variant="primary" :disabled="saving">
            {{ saving ? "Saving..." : "Save" }}
          </BaseButton>
        </div>
      </template>
    </BaseDrawer>
  </AdminPageLayout>
</template>
