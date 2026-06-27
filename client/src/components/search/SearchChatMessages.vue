<script setup lang="ts">
import { computed } from "vue";

import { isExternalHref, safeNavigationHref } from "@/utils/safeUrl";
import type { ChatMessage } from "@/types/search";

interface SourceLink {
  href: string;
  external: boolean;
}

const props = withDefaults(
  defineProps<{
    messages: ChatMessage[];
    loading: boolean;
    showRoleLabels?: boolean;
    emptyMessage?: string;
    sourcesLabel?: string;
    userClass?: string;
    assistantClass?: string;
    roleUserClass?: string;
    roleAssistantClass?: string;
    sourceLinkClass?: string;
    sourceTitleClass?: string;
  }>(),
  {
    showRoleLabels: false,
    emptyMessage: "Search with natural language.",
    sourcesLabel: "Sources",
    userClass: "bg-accent-blue/10 border border-accent-blue/20 text-surface-light ml-6",
    assistantClass: "bg-surface-card border border-surface-border text-surface-sage mr-6",
    roleUserClass: "text-accent-blue",
    roleAssistantClass: "text-accent-violet",
    sourceLinkClass:
      "block rounded-md border border-surface-border/80 bg-surface-dark/80 px-2 py-1.5 hover:border-accent-blue/40 transition-colors",
    sourceTitleClass: "text-xs text-accent-blue font-medium",
  },
);

defineSlots<{
  end?: () => unknown;
}>();

function sourceLink(url: string): SourceLink | null {
  const href = safeNavigationHref(url);
  if (!href) {
    return null;
  }
  return { href, external: isExternalHref(href) };
}

const messageSourceLinks = computed(() =>
  props.messages.map((message) => message.sources?.map((source) => sourceLink(source.url)) ?? []),
);
</script>

<template>
  <div class="space-y-3">
    <p v-if="!messages.length" class="text-surface-mid text-sm text-center py-6">
      {{ emptyMessage }}
    </p>

    <div
      v-for="(msg, index) in messages"
      :key="index"
      :class="[
        'rounded-lg px-3 py-2 text-sm whitespace-pre-wrap leading-relaxed',
        msg.role === 'user' ? userClass : assistantClass,
      ]"
    >
      <span
        v-if="showRoleLabels"
        class="text-[10px] uppercase tracking-wider block mb-1"
        :class="msg.role === 'user' ? roleUserClass : roleAssistantClass"
      >
        {{ msg.role }}
      </span>
      {{ msg.content
      }}<span
        v-if="loading && msg.role === 'assistant' && index === messages.length - 1"
        class="inline-block w-2 h-4 ml-0.5 bg-accent-violet/60 animate-pulse align-middle"
      />

      <div
        v-if="msg.role === 'assistant' && msg.sources?.length"
        class="mt-3 pt-2 border-t border-surface-border/60 space-y-2"
      >
        <p class="text-[10px] uppercase tracking-wider text-surface-mid">
          {{ sourcesLabel }}
        </p>
        <template v-for="(source, sourceIndex) in msg.sources" :key="source.id">
          <a
            v-if="messageSourceLinks[index]?.[sourceIndex]"
            :href="messageSourceLinks[index][sourceIndex]!.href"
            :rel="messageSourceLinks[index][sourceIndex]!.external ? 'noopener noreferrer' : undefined"
            :target="messageSourceLinks[index][sourceIndex]!.external ? '_blank' : undefined"
            :class="sourceLinkClass"
          >
            <span :class="sourceTitleClass">{{ source.title }}</span>
            <span class="text-[10px] text-surface-mid block">{{ source.source_type }}</span>
            <span class="text-[11px] text-surface-mid line-clamp-2">{{ source.snippet }}</span>
          </a>
          <div v-else :class="sourceLinkClass">
            <span :class="sourceTitleClass">{{ source.title }}</span>
            <span class="text-[10px] text-surface-mid block">{{ source.source_type }}</span>
            <span class="text-[11px] text-surface-mid line-clamp-2">{{ source.snippet }}</span>
          </div>
        </template>
      </div>

      <p
        v-else-if="msg.role === 'assistant' && !loading && !msg.sources?.length && msg.content"
        class="mt-2 text-[11px] text-amber-400/90"
      >
        No matching documents — answer may be limited.
      </p>
    </div>

    <slot name="end" />
  </div>
</template>
