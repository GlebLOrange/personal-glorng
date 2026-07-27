<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import NewsArticleContentFields from "@/components/news/NewsArticleContentFields.vue";
import NewsArticleSourceFields from "@/components/news/NewsArticleSourceFields.vue";
import NewsArticleSystemPanel from "@/components/news/NewsArticleSystemPanel.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import {
  NEWS_SUMMARY_MAX_LENGTH,
  NEWS_TAG_LIMIT,
  NEWS_TAG_SET,
  NEWS_TITLE_MAX_LENGTH,
} from "@/constants/news";
import { useNews } from "@/composables/useNews";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import type { NewsArticle, NewsArticleFormData, NewsArticleUpdate } from "@/types";
import { normalizeHttpUrl } from "@/utils/newsForms";

const route = useRoute();
const { toast } = useNotify();
const { can } = usePermissions();
const canWrite = computed(() => can("news", "write"));
const articleId = computed(() => Number(route.params.id));

const {
  article,
  sources,
  detailLoading,
  detailError,
  actionLoading,
  loadAdminArticle,
  loadSources,
  updateArticle,
} = useNews();

useScrollListFingerprint(
  () => `${articleId.value}:${article.value?.id ?? ""}:${article.value?.updated_at ?? ""}`,
);

const form = ref<NewsArticleFormData>(emptyForm());

/** Chrome crumb prefers public path shape `news/<slug>` once known. */
const chromeTitle = computed(() => {
  const slug = form.value.slug.trim();
  return slug ? `news/${slug}` : "edit news article";
});

function emptyForm(): NewsArticleFormData {
  return {
    slug: "",
    status: "draft",
    source_id: null,
    source_name: "",
    source_url: "",
    source_feed_url: "",
    source_published_at: "",
    original_title: "",
    title: "",
    summary: "",
    bullets: [],
    tags: "",
    language: "en",
    published_at: "",
    telegram_message_id: "",
    ai_model: "",
    ai_input_hash: "",
    ingest_error: "",
  };
}

function formFromArticle(item: NewsArticle): NewsArticleFormData {
  return {
    slug: item.slug,
    status: item.status,
    source_id: item.source_id,
    source_name: item.source_name,
    source_url: item.source_url,
    source_feed_url: item.source_feed_url,
    source_published_at: item.source_published_at?.slice(0, 16) ?? "",
    original_title: item.original_title,
    title: item.title,
    summary: item.summary,
    bullets: [],
    tags: item.tags.join(", "),
    language: item.language,
    published_at: item.published_at?.slice(0, 16) ?? "",
    telegram_message_id: item.telegram_message_id?.toString() ?? "",
    ai_model: item.ai_model ?? "",
    ai_input_hash: item.ai_input_hash ?? "",
    ingest_error: item.ingest_error ?? "",
  };
}

function parsedTags(): string[] {
  return form.value.tags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function normalizedDateTime(value: string): string | null {
  if (!value.trim()) return null;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString();
}

function optionalText(value: string): string | null {
  const trimmed = value.trim();
  return trimmed || null;
}

function sourceFeedUrlPayload(): string | undefined {
  return normalizeHttpUrl(form.value.source_feed_url) ?? undefined;
}

function dateIsInvalid(value: string, normalizedValue: string | null): boolean {
  return Boolean(value.trim()) && normalizedValue === null;
}

function validateForm(): boolean {
  const title = form.value.title.trim();
  const summary = form.value.summary.trim();
  const tags = parsedTags();

  if (!canWrite.value) return false;
  if (!form.value.slug.trim()) {
    toast("Slug is required", "error");
    return false;
  }
  if (!title) {
    toast("Title is required", "error");
    return false;
  }
  if (title.length > NEWS_TITLE_MAX_LENGTH) {
    toast(`Title must be ${NEWS_TITLE_MAX_LENGTH} characters or fewer`, "error");
    return false;
  }
  if (!summary) {
    toast("Summary is required", "error");
    return false;
  }
  if (summary.length > NEWS_SUMMARY_MAX_LENGTH) {
    toast(`Summary must be ${NEWS_SUMMARY_MAX_LENGTH} characters or fewer`, "error");
    return false;
  }
  if (!normalizeHttpUrl(form.value.source_url)) {
    toast("Source URL must start with http:// or https://", "error");
    return false;
  }
  if (form.value.source_feed_url.trim() && !sourceFeedUrlPayload()) {
    toast("Source feed/home URL must start with http:// or https://", "error");
    return false;
  }
  if (tags.length < 1) {
    toast("Add at least one tag", "error");
    return false;
  }
  if (tags.length > NEWS_TAG_LIMIT) {
    toast(`Choose no more than ${NEWS_TAG_LIMIT} tags`, "error");
    return false;
  }
  if (tags.some((tag) => !NEWS_TAG_SET.has(tag))) {
    toast("Choose only supported news tags", "error");
    return false;
  }
  if (
    dateIsInvalid(
      form.value.source_published_at,
      normalizedDateTime(form.value.source_published_at),
    )
  ) {
    toast("Source published date is invalid", "error");
    return false;
  }
  return true;
}

function buildUpdatePayload(): NewsArticleUpdate {
  return {
    slug: form.value.slug.trim(),
    status: form.value.status,
    source_id: form.value.source_id,
    source_name: optionalText(form.value.source_name) ?? undefined,
    source_url: normalizeHttpUrl(form.value.source_url) ?? form.value.source_url.trim(),
    source_feed_url: sourceFeedUrlPayload(),
    source_published_at: normalizedDateTime(form.value.source_published_at),
    original_title: form.value.original_title.trim() || form.value.title.trim(),
    title: form.value.title.trim(),
    summary: form.value.summary.trim(),
    tags: parsedTags(),
    language: form.value.language.trim() || "en",
  };
}

async function loadCurrentArticle(): Promise<void> {
  if (!Number.isInteger(articleId.value) || articleId.value <= 0) return;
  await loadAdminArticle(articleId.value);
  if (article.value) form.value = formFromArticle(article.value);
}

async function saveArticle(): Promise<void> {
  if (!article.value || !validateForm()) return;
  const updated = await updateArticle(article.value.id, buildUpdatePayload());
  if (!updated) return;
  article.value = updated;
  form.value = formFromArticle(updated);
}

onMounted(async () => {
  await Promise.all([loadCurrentArticle(), loadSources()]);
});

watch(articleId, () => {
  void loadCurrentArticle();
});
</script>

<template>
  <AdminPageLayout hub="tools" :title="chromeTitle" max-width="xl" back-to="/news?manage=1">
    <header v-if="canWrite && article" class="page-intro">
      <div class="flex flex-wrap gap-2">
        <BaseButton variant="success" :disabled="actionLoading" @click="saveArticle">
          {{ actionLoading ? "saving..." : "save article" }}
        </BaseButton>
      </div>
    </header>

    <div class="min-w-0">
      <Card v-if="!Number.isInteger(articleId) || articleId <= 0" role="alert">
        <p class="text-sm text-status-warning">Invalid news article id.</p>
      </Card>

      <Card
        v-else-if="detailLoading"
        class="h-96 animate-pulse"
        aria-busy="true"
        aria-label="Loading news article"
      />

      <Card v-else-if="detailError" role="alert">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p class="text-sm text-status-warning">{{ detailError }}</p>
          <BaseButton
            variant="ghost"
            size="sm"
            class="gap-1.5"
            @click="loadCurrentArticle"
          >
            <RefreshIcon class-name="size-3.5" />
            retry
          </BaseButton>
        </div>
      </Card>

      <form
        v-else-if="article"
        class="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]"
        @submit.prevent="saveArticle"
      >
        <div class="space-y-6">
          <NewsArticleContentFields v-model="form" :can-write="canWrite" />
          <NewsArticleSourceFields v-model="form" :can-write="canWrite" :sources="sources" />
        </div>

        <NewsArticleSystemPanel :article="article" :form="form" :can-write="canWrite" />
      </form>
    </div>
  </AdminPageLayout>
</template>
