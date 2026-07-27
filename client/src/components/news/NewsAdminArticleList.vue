<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
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
      <div
        class="mb-3 flex flex-wrap items-center justify-between gap-2 rounded-md px-2.5 py-1.5 text-xs"
        :class="newsStatusClass(item.status)"
        :aria-label="item.status"
      >
        <div class="flex min-w-0 flex-wrap items-center gap-2">
          <time :datetime="item.published_at ?? item.created_at">
            {{ formatNewsDate(item.published_at ?? item.created_at) }}
          </time>
          <span v-if="item.telegram_message_id" class="text-accent-blue">
            Telegram #{{ item.telegram_message_id }}
          </span>
        </div>
        <a
          v-if="safeNavigationHref(item.source_url)"
          :href="safeNavigationHref(item.source_url) ?? '#'"
          target="_blank"
          rel="noopener noreferrer"
          class="shrink-0 text-accent-blue hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
          @click.stop
        >
          {{ item.source_name }}
        </a>
        <span v-else class="shrink-0 text-accent-blue">{{ item.source_name }}</span>
      </div>

      <h2 class="card-title mb-2 break-words">{{ item.title }}</h2>
      <p class="text-sm text-surface-mid mb-3 break-words">{{ item.summary }}</p>

      <div class="mb-4 flex flex-wrap gap-2">
        <span
          v-for="tag in item.tags"
          :key="tag"
          class="rounded bg-accent-blue/10 px-2.5 py-1 text-xs text-accent-blue"
        >
          #{{ tag }}
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
          @click="emit('setStatus', item.id, 'private')"
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
      </div>
    </Card>
  </section>
</template>
