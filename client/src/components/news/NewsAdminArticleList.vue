<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { Card } from "@/components/ui/card";
import { newsStatusClass } from "@/constants/filterColors";
import { newsStatusLabel } from "@/constants/news";
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
      <div class="mb-2 flex min-w-0 flex-wrap items-center gap-2 text-xs">
        <a
          v-if="safeNavigationHref(item.source_url)"
          :href="safeNavigationHref(item.source_url) ?? '#'"
          target="_blank"
          rel="noopener noreferrer"
          class="shrink-0 text-accent-coral hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50 rounded"
          @click.stop
        >
          {{ item.source_name }}
        </a>
        <span v-else class="shrink-0 text-accent-coral">{{ item.source_name }}</span>
        <time
          class="text-datetime shrink-0 whitespace-nowrap lowercase"
          :datetime="item.published_at ?? item.created_at"
        >
          {{ formatNewsDate(item.published_at ?? item.created_at) }}
        </time>
        <StatusBadge
          :label="newsStatusLabel(item.status)"
          :class-name="newsStatusClass(item.status)"
        />
        <span v-if="item.telegram_message_id" class="shrink-0 text-accent-coral">
          Telegram #{{ item.telegram_message_id }}
        </span>
        <div v-if="item.tags.length" class="ml-auto flex min-w-0 flex-wrap justify-end gap-2">
          <span
            v-for="tag in item.tags"
            :key="tag"
            class="rounded bg-accent-coral/10 px-2.5 py-1 text-xs text-accent-coral"
          >
            #{{ tag }}
          </span>
        </div>
      </div>

      <h2 class="card-title mb-2 min-w-0 break-words">{{ item.title }}</h2>

      <p class="mb-2 break-words text-sm text-surface-mid">{{ item.summary }}</p>

      <div
        v-if="canWrite"
        class="flex w-full flex-wrap items-center justify-between gap-2"
        @click.stop
        @keydown.stop
      >
        <BaseButton
          v-if="item.status !== 'published'"
          variant="save"
          size="sm"
          :disabled="actionLoading"
          @click="emit('setStatus', item.id, 'published')"
        >
          publish
        </BaseButton>
        <BaseButton
          v-else
          variant="ghost"
          quiet
          size="sm"
          :disabled="actionLoading"
          @click="emit('setStatus', item.id, 'private')"
        >
          unpublish
        </BaseButton>
        <BaseButton
          variant="ghost"
          quiet
          size="sm"
          class="ml-auto"
          :disabled="actionLoading"
          @click="emit('repost', item.id)"
        >
          repost telegram
        </BaseButton>
      </div>
    </Card>
  </section>
</template>
