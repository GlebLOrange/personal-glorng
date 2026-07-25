<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { Card } from "@/components/ui/card";
import { newsStatusClass } from "@/constants/filterColors";
import { formatNewsDate } from "@/composables/useNews";
import type { NewsArticle, NewsStatus } from "@/types";
import { safeNavigationHref } from "@/utils/safeUrl";

defineProps<{
  articles: NewsArticle[];
  canWrite: boolean;
  actionLoading: boolean;
}>();

const emit = defineEmits<{
  edit: [article: NewsArticle];
  setStatus: [articleId: number, status: NewsStatus];
  repost: [articleId: number];
}>();
</script>

<template>
  <section class="space-y-3 min-w-0">
    <Card
      v-for="item in articles"
      :key="item.id"
      as="article"
      variant="compact"
      class="min-w-0"
      :class="canWrite ? 'cursor-pointer' : undefined"
      :hoverable="canWrite"
      :interactive="canWrite"
      :role="canWrite ? 'button' : undefined"
      :tabindex="canWrite ? 0 : undefined"
      @click="canWrite ? emit('edit', item) : undefined"
      @keydown.enter.prevent="canWrite ? emit('edit', item) : undefined"
    >
      <div class="mb-3 flex flex-wrap items-center gap-2 text-xs text-surface-muted">
        <StatusBadge :label="item.status" :class-name="newsStatusClass(item.status)" />
        <span aria-hidden="true">/</span>
        <span>{{ item.source_name }}</span>
        <span aria-hidden="true">/</span>
        <time :datetime="item.published_at ?? item.created_at">
          {{ formatNewsDate(item.published_at ?? item.created_at) }}
        </time>
        <span v-if="item.telegram_message_id" class="text-accent-blue">
          Telegram #{{ item.telegram_message_id }}
        </span>
      </div>

      <h2 class="card-title mb-2 break-words">{{ item.title }}</h2>
      <p class="text-sm text-surface-mid mb-3 break-words">{{ item.summary }}</p>

      <div class="mb-4 flex flex-wrap gap-2">
        <span
          v-for="theme in item.themes"
          :key="theme"
          class="rounded border border-surface-border px-2 py-1 text-xs text-surface-mid"
        >
          {{ theme }}
        </span>
      </div>

      <div class="flex flex-wrap gap-2" @click.stop @keydown.stop>
        <BaseButton
          v-if="canWrite && item.status !== 'published'"
          variant="success"
          size="sm"
          :disabled="actionLoading"
          @click="emit('setStatus', item.id, 'published')"
        >
          publish
        </BaseButton>
        <BaseButton
          v-if="canWrite && item.status === 'published'"
          variant="ghost"
          quiet
          size="sm"
          :disabled="actionLoading"
          @click="emit('setStatus', item.id, 'unpublished')"
        >
          unpublish
        </BaseButton>
        <BaseButton
          v-if="canWrite"
          variant="ghost"
          quiet
          size="sm"
          :disabled="actionLoading"
          @click="emit('repost', item.id)"
        >
          repost telegram
        </BaseButton>
        <a
          v-if="safeNavigationHref(item.source_url)"
          :href="safeNavigationHref(item.source_url) ?? '#'"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center rounded-lg border border-transparent bg-status-success/3 px-3 py-1.5 text-xs font-medium text-status-success hover:border-status-success/40 hover:bg-status-success/15"
        >
          source
        </a>
      </div>
    </Card>
  </section>
</template>
