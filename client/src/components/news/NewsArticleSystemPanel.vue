<script setup lang="ts">
import { computed } from "vue";

import { Card } from "@/components/ui/card";
import { formatNewsDate } from "@/composables/useNews";
import { newsStatusLabel } from "@/constants/news";
import type { NewsArticle, NewsArticleFormData } from "@/types";

const props = defineProps<{
  article: NewsArticle;
  form: NewsArticleFormData;
  canWrite: boolean;
}>();

const previewTags = computed(() =>
  props.form.tags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean),
);
</script>

<template>
  <aside class="space-y-6">
    <Card>
      <h2 class="card-title mb-4">system fields</h2>
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
          <dd class="font-data text-surface-light">
            {{ article.telegram_message_id ?? "none" }}
          </dd>
        </div>
      </dl>
    </Card>

    <Card>
      <h2 class="card-title mb-4">current preview</h2>
      <p class="mb-2 text-xs text-surface-muted">
        {{ newsStatusLabel(form.status) }} / {{ form.source_name || "unknown source" }}
      </p>
      <h3 class="mb-3 text-lg font-semibold text-surface-light">
        {{ form.title || "Untitled" }}
      </h3>
      <p class="text-sm text-surface-mid">{{ form.summary || "No summary yet." }}</p>
      <div class="mt-4 flex flex-wrap gap-2">
        <span
          v-for="tag in previewTags"
          :key="tag"
          class="rounded bg-accent-blue/10 px-2.5 py-1 text-xs text-accent-blue"
        >
          #{{ tag }}
        </span>
      </div>
    </Card>

    <Card v-if="!canWrite">
      <p class="text-sm text-surface-mid">
        You have `news:read`, so this page is read-only. Saving requires `news:write`.
      </p>
    </Card>
  </aside>
</template>
