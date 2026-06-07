<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { api } from "@/composables/useApi";
import { useSearchChat } from "@/composables/useSearchChat";
import { useNotify } from "@/composables/useNotify";
import { isAiSearchEnabled } from "@/utils/featureFlags";
import { getApiErrorMessage } from "@/types/api";

interface SearchConfig {
  enabled: boolean;
  configured: boolean;
}

const open = ref(false);
const chatEnd = ref<HTMLElement | null>(null);
const searchConfig = ref<SearchConfig | null>(null);
const configLoading = ref(true);
const { toast } = useNotify();

const isAvailable = computed(
  () => isAiSearchEnabled() && Boolean(searchConfig.value?.enabled && searchConfig.value?.configured),
);

const { messages, input, loading, send, clear } = useSearchChat({
  endpoint: "/api/search/chat",
  onError: (message) => toast(message, "error"),
});

function scrollToBottom(): void {
  nextTick(() => chatEnd.value?.scrollIntoView({ behavior: "smooth" }));
}

async function loadConfig(): Promise<void> {
  configLoading.value = true;
  try {
    const { data } = await api.get<SearchConfig>("/search/config");
    searchConfig.value = data;
  } catch (err) {
    searchConfig.value = { enabled: false, configured: false };
    console.error(getApiErrorMessage(err, "Failed to load search config"));
  } finally {
    configLoading.value = false;
  }
}

async function handleSend(): Promise<void> {
  try {
    await send();
    scrollToBottom();
  } catch {
    // toast handled in composable
  }
}

function toggle(): void {
  open.value = !open.value;
  if (open.value) {
    scrollToBottom();
  }
}

onMounted(() => {
  void loadConfig();
});
</script>

<template>
  <div v-if="isAiSearchEnabled()" class="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-3">
    <div
      v-if="open"
      class="w-[min(24rem,calc(100vw-3rem))] rounded-xl border border-surface-border bg-surface-dark shadow-2xl flex flex-col max-h-[70vh]"
    >
      <div class="flex items-center justify-between px-4 py-3 border-b border-surface-border">
        <div>
          <p class="text-sm font-medium text-surface-light">Portfolio search</p>
          <p class="text-[11px] text-surface-mid">Ask about skills, projects, and recipes</p>
        </div>
        <BaseButton variant="ghost" size="sm" type="button" @click="toggle">Close</BaseButton>
      </div>

      <div class="flex-1 overflow-y-auto px-4 py-3 space-y-3">
        <p v-if="!messages.length" class="text-surface-mid text-sm text-center py-6">
          Search the portfolio with natural language.
        </p>

        <div
          v-for="(msg, i) in messages"
          :key="i"
          :class="[
            'rounded-lg px-3 py-2 text-sm whitespace-pre-wrap',
            msg.role === 'user'
              ? 'bg-accent-blue/10 border border-accent-blue/20 text-surface-light ml-6'
              : 'bg-surface-card border border-surface-border text-surface-sage mr-6',
          ]"
        >
          {{ msg.content }}
          <span
            v-if="loading && msg.role === 'assistant' && i === messages.length - 1"
            class="inline-block w-2 h-4 ml-0.5 bg-accent-violet/60 animate-pulse align-middle"
          />

          <div
            v-if="msg.role === 'assistant' && msg.sources?.length"
            class="mt-3 pt-2 border-t border-surface-border/60 space-y-2"
          >
            <p class="text-[10px] uppercase tracking-wider text-surface-mid">Sources</p>
            <a
              v-for="source in msg.sources"
              :key="source.id"
              :href="source.url"
              class="block rounded-md border border-surface-border/80 bg-surface-dark/80 px-2 py-1.5 hover:border-accent-blue/40 transition-colors"
            >
              <span class="text-xs text-accent-blue font-medium">{{ source.title }}</span>
              <span class="text-[10px] text-surface-mid block">{{ source.source_type }}</span>
              <span class="text-[11px] text-surface-mid line-clamp-2">{{ source.snippet }}</span>
            </a>
          </div>

          <p
            v-else-if="msg.role === 'assistant' && !loading && !msg.sources?.length && msg.content"
            class="mt-2 text-[11px] text-amber-400/90"
          >
            No matching documents — answer may be limited.
          </p>
        </div>
        <div ref="chatEnd" />
      </div>

      <form class="flex gap-2 border-t border-surface-border p-3" @submit.prevent="handleSend">
        <input
          v-model="input"
          type="text"
          placeholder="What technologies do you use?"
          class="flex-1 bg-surface-card border border-surface-border rounded-lg px-3 py-2 text-sm text-surface-light focus:outline-none focus:border-accent-blue"
          :disabled="!isAvailable || loading"
        />
        <BaseButton variant="primary" :disabled="loading || !input.trim() || !isAvailable">
          Send
        </BaseButton>
      </form>

      <div class="px-3 pb-3 flex justify-between items-center">
        <span v-if="configLoading" class="text-[11px] text-surface-mid">Loading…</span>
        <span v-else-if="!isAvailable" class="text-[11px] text-amber-400/90">Search unavailable</span>
        <span v-else class="text-[11px] text-surface-mid">Indexed public content only</span>
        <BaseButton variant="ghost" size="sm" type="button" :disabled="loading" @click="clear">
          Clear
        </BaseButton>
      </div>
    </div>

    <BaseButton
      v-if="!open"
      variant="primary"
      type="button"
      class="shadow-lg"
      :disabled="configLoading || !isAvailable"
      @click="toggle"
    >
      Ask portfolio
    </BaseButton>
  </div>
</template>
