<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { SELECT_CLASS } from "@/constants/formClasses";
import { formatNewsDate, useNews } from "@/composables/useNews";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
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

const form = ref<NewsArticleFormData>(emptyForm());

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
    bullets: ["", ""],
    themes: "",
    language: "en",
    published_at: "",
    telegram_message_id: "",
    ai_model: "",
    ai_input_hash: "",
    ingest_error: "",
  };
}

function formFromArticle(item: NewsArticle): NewsArticleFormData {
  const bullets = item.bullets.length ? [...item.bullets] : ["", ""];
  while (bullets.length < 2) bullets.push("");
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
    bullets,
    themes: item.themes.join(", "),
    language: item.language,
    published_at: item.published_at?.slice(0, 16) ?? "",
    telegram_message_id: item.telegram_message_id?.toString() ?? "",
    ai_model: item.ai_model ?? "",
    ai_input_hash: item.ai_input_hash ?? "",
    ingest_error: item.ingest_error ?? "",
  };
}

function parsedThemes(): string[] {
  return form.value.themes
    .split(",")
    .map((theme) => theme.trim())
    .filter(Boolean);
}

function parsedBullets(): string[] {
  return form.value.bullets.map((bullet) => bullet.trim()).filter(Boolean);
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

function telegramMessageIdPayload(): number | null {
  const value = form.value.telegram_message_id.trim();
  if (!value) return null;
  const messageId = Number(value);
  return Number.isInteger(messageId) && messageId >= 0 ? messageId : Number.NaN;
}

function sourceFeedUrlPayload(): string | undefined {
  return normalizeHttpUrl(form.value.source_feed_url) ?? undefined;
}

function dateIsInvalid(value: string, normalizedValue: string | null): boolean {
  return Boolean(value.trim()) && normalizedValue === null;
}

function validateForm(): boolean {
  if (!canWrite.value) return false;
  if (!form.value.slug.trim()) {
    toast("Slug is required", "error");
    return false;
  }
  if (!form.value.title.trim()) {
    toast("Title is required", "error");
    return false;
  }
  if (!form.value.summary.trim()) {
    toast("Summary is required", "error");
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
  if (parsedBullets().length < 2) {
    toast("Add at least two key points", "error");
    return false;
  }
  if (parsedThemes().length < 1) {
    toast("Add at least one theme", "error");
    return false;
  }
  if (dateIsInvalid(form.value.source_published_at, normalizedDateTime(form.value.source_published_at))) {
    toast("Source published date is invalid", "error");
    return false;
  }
  if (dateIsInvalid(form.value.published_at, normalizedDateTime(form.value.published_at))) {
    toast("Published date is invalid", "error");
    return false;
  }
  if (Number.isNaN(telegramMessageIdPayload())) {
    toast("Telegram message ID must be a whole number", "error");
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
    bullets: parsedBullets(),
    themes: parsedThemes(),
    language: form.value.language.trim() || "en",
    published_at: normalizedDateTime(form.value.published_at),
    telegram_message_id: telegramMessageIdPayload(),
    ai_model: optionalText(form.value.ai_model),
    ai_input_hash: optionalText(form.value.ai_input_hash),
    ingest_error: optionalText(form.value.ingest_error),
  };
}

function updateBullet(index: number, value: string): void {
  const bullets = [...form.value.bullets];
  bullets[index] = value;
  form.value.bullets = bullets;
}

function addBullet(): void {
  if (form.value.bullets.length >= 5) return;
  form.value.bullets = [...form.value.bullets, ""];
}

function removeBullet(index: number): void {
  if (form.value.bullets.length <= 2) return;
  form.value.bullets = form.value.bullets.filter((_, i) => i !== index);
}

function applySource(sourceId: number | null): void {
  const source = sources.value.find((item) => item.id === sourceId);
  form.value.source_id = sourceId;
  if (!source) return;
  form.value.source_name = source.name;
  form.value.source_feed_url = source.feed_url;
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
  <AdminPageLayout title="edit news article" max-width="xl">
    <div class="mb-6 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
      <RouterLink to="/admin/tools/news" class="nav-link-accent text-sm">
        Back to NEWS
      </RouterLink>
      <BaseButton
        v-if="canWrite && article"
        variant="primary"
        :disabled="actionLoading"
        @click="saveArticle"
      >
        {{ actionLoading ? "Saving..." : "Save article" }}
      </BaseButton>
    </div>

    <BaseCard v-if="!Number.isInteger(articleId) || articleId <= 0" role="alert">
      <p class="text-sm text-accent-golden">Invalid news article id.</p>
    </BaseCard>

    <div
      v-else-if="detailLoading"
      class="h-96 rounded-lg border border-surface-border bg-surface-card animate-pulse"
      aria-busy="true"
      aria-label="Loading news article"
    />

    <BaseCard v-else-if="detailError" role="alert">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-sm text-accent-golden">{{ detailError }}</p>
        <BaseButton variant="ghost" size="sm" @click="loadCurrentArticle">Retry</BaseButton>
      </div>
    </BaseCard>

    <form v-else-if="article" class="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]" @submit.prevent="saveArticle">
      <div class="space-y-6">
        <BaseCard>
          <h2 class="card-title mb-4">Article</h2>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <BaseInput v-model="form.slug" label="Slug" :disabled="!canWrite" />
            <label class="flex flex-col gap-1 text-sm text-surface-mid">
              Status
              <select
                v-model="form.status"
                :class="SELECT_CLASS"
                :disabled="!canWrite"
              >
                <option value="draft">draft</option>
                <option value="published">published</option>
                <option value="unpublished">unpublished</option>
                <option value="failed">failed</option>
              </select>
            </label>
            <BaseInput v-model="form.title" label="Title" :disabled="!canWrite" />
            <BaseInput v-model="form.original_title" label="Original title" :disabled="!canWrite" />
            <BaseInput v-model="form.language" label="Language" :disabled="!canWrite" />
            <BaseInput v-model="form.themes" label="Themes" placeholder="world, business" :disabled="!canWrite" />
          </div>
          <div class="mt-4">
            <BaseTextarea v-model="form.summary" label="Summary" :rows="4" :disabled="!canWrite" />
          </div>
        </BaseCard>

        <BaseCard>
          <div class="mb-4 flex items-center justify-between gap-3">
            <h2 class="card-title">Key points</h2>
            <BaseButton
              v-if="canWrite"
              variant="ghost"
              size="sm"
              type="button"
              :disabled="form.bullets.length >= 5"
              @click="addBullet"
            >
              + bullet
            </BaseButton>
          </div>
          <div class="space-y-3">
            <div v-for="(_, index) in form.bullets" :key="index" class="flex items-start gap-2">
              <span class="pt-2 text-sm text-surface-muted">{{ index + 1 }}.</span>
              <input
                :value="form.bullets[index]"
                class="w-full rounded-lg border border-surface-border bg-surface-dark px-4 py-2 text-sm text-surface-light transition-colors placeholder:text-surface-mid/50 focus:outline-none focus:border-accent-blue disabled:opacity-60"
                :disabled="!canWrite"
                :placeholder="`Key point ${index + 1}`"
                @input="updateBullet(index, ($event.target as HTMLInputElement).value)"
              />
              <BaseButton
                v-if="canWrite && form.bullets.length > 2"
                variant="ghost"
                size="sm"
                type="button"
                aria-label="Remove bullet"
                @click="removeBullet(index)"
              >
                &times;
              </BaseButton>
            </div>
          </div>
        </BaseCard>

        <BaseCard>
          <h2 class="card-title mb-4">Source</h2>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <label class="flex flex-col gap-1 text-sm text-surface-mid">
              Source
              <select
                :value="form.source_id ?? ''"
                :class="SELECT_CLASS"
                :disabled="!canWrite"
                @change="applySource(Number(($event.target as HTMLSelectElement).value) || null)"
              >
                <option value="">Auto from URL host</option>
                <option v-for="source in sources" :key="source.id" :value="source.id">
                  {{ source.name }}{{ source.host ? ` (${source.host})` : "" }}
                </option>
              </select>
            </label>
            <BaseInput v-model="form.source_name" label="Source name" :disabled="!canWrite" />
            <BaseInput v-model="form.source_url" label="Article URL" type="url" :disabled="!canWrite" />
            <BaseInput v-model="form.source_feed_url" label="Source feed/home URL" type="url" :disabled="!canWrite" />
            <BaseInput
              v-model="form.source_published_at"
              label="Source published at"
              type="datetime-local"
              :disabled="!canWrite"
            />
            <BaseInput
              v-model="form.published_at"
              label="Published at"
              type="datetime-local"
              :disabled="!canWrite"
            />
          </div>
        </BaseCard>

        <BaseCard>
          <h2 class="card-title mb-4">Admin metadata</h2>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <BaseInput
              v-model="form.telegram_message_id"
              label="Telegram message ID"
              inputmode="numeric"
              :disabled="!canWrite"
            />
            <BaseInput v-model="form.ai_model" label="AI model" :disabled="!canWrite" />
            <BaseInput v-model="form.ai_input_hash" label="AI input hash" :disabled="!canWrite" />
          </div>
          <div class="mt-4">
            <BaseTextarea v-model="form.ingest_error" label="Ingest error" :rows="3" :disabled="!canWrite" />
          </div>
        </BaseCard>
      </div>

      <aside class="space-y-6">
        <BaseCard>
          <h2 class="card-title mb-4">System fields</h2>
          <dl class="space-y-3 text-sm">
            <div>
              <dt class="text-surface-muted">ID</dt>
              <dd class="font-data text-surface-light">{{ article.id }}</dd>
            </div>
            <div>
              <dt class="text-surface-muted">Created</dt>
              <dd class="text-surface-light">{{ formatNewsDate(article.created_at) }}</dd>
            </div>
            <div>
              <dt class="text-surface-muted">Updated</dt>
              <dd class="text-surface-light">{{ formatNewsDate(article.updated_at) }}</dd>
            </div>
            <div>
              <dt class="text-surface-muted">Source ID</dt>
              <dd class="font-data text-surface-light">{{ article.source_id ?? "none" }}</dd>
            </div>
            <div>
              <dt class="text-surface-muted">Telegram message</dt>
              <dd class="font-data text-surface-light">{{ article.telegram_message_id ?? "none" }}</dd>
            </div>
          </dl>
        </BaseCard>

        <BaseCard>
          <h2 class="card-title mb-4">Current preview</h2>
          <p class="mb-2 text-xs text-surface-muted">{{ form.status }} / {{ form.source_name || "unknown source" }}</p>
          <h3 class="mb-3 text-lg font-semibold text-surface-light">{{ form.title || "Untitled" }}</h3>
          <p class="text-sm text-surface-mid">{{ form.summary || "No summary yet." }}</p>
          <div class="mt-4 flex flex-wrap gap-2">
            <span
              v-for="theme in parsedThemes()"
              :key="theme"
              class="rounded border border-surface-border px-2 py-1 text-xs text-surface-mid"
            >
              {{ theme }}
            </span>
          </div>
        </BaseCard>

        <BaseCard v-if="!canWrite">
          <p class="text-sm text-surface-mid">
            You have `news:read`, so this page is read-only. Saving requires `news:write`.
          </p>
        </BaseCard>
      </aside>
    </form>
  </AdminPageLayout>
</template>
