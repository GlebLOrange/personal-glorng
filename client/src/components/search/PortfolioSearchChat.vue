<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";

import SearchChatMessages from "@/components/search/SearchChatMessages.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { useChatConfig } from "@/composables/useChatConfig";
import { useSearchChat } from "@/composables/useSearchChat";
import { useNotify } from "@/composables/useNotify";
import { isAiSearchEnabled } from "@/utils/featureFlags";
import type { SearchConfig } from "@/types/search";

const open = ref(false);
const chatEnd = ref<HTMLElement | null>(null);
const { toast } = useNotify();

const showWidget = computed(() => isAiSearchEnabled());

const {
  loading: configLoading,
  loadConfig,
  isReady,
} = useChatConfig<SearchConfig>({
  path: "/search/config",
  fallback: { enabled: false, configured: false },
});

const isAvailable = computed(() => showWidget.value && isReady.value);

const { messages, input, loading, send, clear } = useSearchChat({
  endpoint: "/api/search/chat",
  onError: (message) => toast(message, "error"),
});

function scrollToBottom(): void {
  nextTick(() => chatEnd.value?.scrollIntoView({ behavior: "smooth" }));
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
  if (showWidget.value) {
    void loadConfig();
  }
});
</script>

<template>
  <div v-if="showWidget" class="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-3">
    <div
      v-if="open"
      class="w-[min(24rem,calc(100vw-3rem))] rounded-xl border border-surface-border bg-surface-dark shadow-2xl flex flex-col max-h-[70vh]"
    >
      <div class="flex items-center justify-between px-4 py-3 border-b border-surface-border">
        <div>
          <p class="text-sm font-medium text-surface-light">Portfolio search</p>
          <p class="text-xs text-surface-mid">Ask about skills, projects, and recipes</p>
        </div>
        <BaseButton variant="ghost" size="sm" type="button" @click="toggle">Close</BaseButton>
      </div>

      <div class="flex-1 overflow-y-auto px-4 py-3">
        <SearchChatMessages
          :messages="messages"
          :loading="loading"
          empty-message="Search the portfolio with natural language."
        >
          <template #end>
            <div ref="chatEnd" />
          </template>
        </SearchChatMessages>
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
        <span v-if="configLoading" class="text-xs text-surface-mid">Loading…</span>
        <span v-else-if="!isAvailable" class="text-xs text-amber-400/90">Search unavailable</span>
        <span v-else class="text-xs text-surface-mid">Indexed public content only</span>
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
