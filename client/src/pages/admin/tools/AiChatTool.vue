<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";

import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import SearchChatMessages from "@/components/search/SearchChatMessages.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import { useChatConfig } from "@/composables/useChatConfig";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import { useSearchChat } from "@/composables/useSearchChat";
import { useAuthStore } from "@/stores/auth";
import type { AdminChatConfig } from "@/types/search";

type AiChatTab = "chat" | "settings";

const AI_CHAT_TABS = [
  { id: "chat", label: "chat" },
  { id: "settings", label: "settings" },
] as const;

const PROVIDER_EXAMPLES = [
  {
    name: "Gemini",
    env: `GEMINI_API_KEY=AIza...
GEMINI_CHAT_MODEL=gemini-3.5-flash`,
  },
] as const;

const activeTab = ref<AiChatTab>("chat");
const chatEnd = ref<HTMLElement | null>(null);
const { toast } = useNotify();
const { can } = usePermissions();
const canSend = computed(() => can("ai-chat", "write"));

const {
  config: chatConfig,
  loading: configLoading,
  loadConfig,
  isReady,
} = useChatConfig<AdminChatConfig>({
  path: "/tools/ai-chat/config",
  fallback: {
    enabled: false,
    configured: false,
    model: "",
    provider: "",
    base_url: null,
  },
  onError: (message) => toast(message, "error"),
});

const { messages, input, loading, send, clear } = useSearchChat({
  endpoint: "/api/tools/ai-chat",
  onError: (message) => toast(message, "error"),
  beforeSend: async () => {
    const auth = useAuthStore();
    if (!auth.isAuthenticated) {
      toast("Not authenticated", "error");
      return false;
    }
    if (!canSend.value) {
      toast("You don't have permission to send messages", "error");
      return false;
    }
    if (!isReady.value) {
      toast("AI chat is not configured — check Settings", "error");
      activeTab.value = "settings";
      return false;
    }
    return true;
  },
});

const providerLabel = computed(() => chatConfig.value?.provider ?? "…");
const modelLabel = computed(() => chatConfig.value?.model ?? "…");

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

onMounted(() => {
  void loadConfig().then(() => {
    if (chatConfig.value && !chatConfig.value.configured) {
      activeTab.value = "settings";
    }
  });
});
</script>

<template>
  <AdminPageLayout title="ai chat">
    <AdminTabBar v-model="activeTab" :tabs="[...AI_CHAT_TABS]" />

    <Card v-if="activeTab === 'chat'" class="flex flex-col h-[65vh]">
      <div class="flex items-center gap-3 mb-4 pb-4 border-b border-surface-border">
        <span class="text-surface-mid text-xs uppercase tracking-wider">
          {{ providerLabel }}
        </span>
        <span class="text-surface-mid/60 text-xs">·</span>
        <span class="text-surface-mid text-xs">{{ modelLabel }}</span>
        <span class="text-surface-mid/60 text-xs">· personal search</span>
        <span v-if="!configLoading && !isReady" class="ml-auto text-xs text-status-warning/90">
          not configured
        </span>
        <span v-else-if="!canSend" class="ml-auto text-xs text-status-warning/90">
          read-only
        </span>
      </div>

      <div class="flex-1 overflow-y-auto mb-4 pr-1">
        <SearchChatMessages
          :messages="messages"
          :loading="loading"
          show-role-labels
          empty-message="Search your indexed content — tasks, recipes, expenses, and more."
          sources-label="Searching your indexed content"
          user-class="bg-accent-blue/10 border border-accent-blue/20 text-surface-light ml-8"
          assistant-class="bg-surface-dark border border-surface-border text-surface-sage mr-8"
          source-link-class="block rounded-md border border-surface-border/80 bg-surface-card/60 px-3 py-2 hover:border-accent-violet/40 transition-colors"
          source-title-class="text-xs text-accent-violet font-medium"
        >
          <template #end>
            <div ref="chatEnd" />
          </template>
        </SearchChatMessages>
      </div>

      <form class="flex gap-3 border-t border-surface-border pt-4" @submit.prevent="handleSend">
        <textarea
          v-model="input"
          rows="2"
          placeholder="Search tasks, recipes, projects..."
          class="flex-1 bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50 resize-none"
          @keydown.enter.exact.prevent="handleSend"
        />
        <div class="flex flex-col gap-2">
          <BaseButton variant="primary" :disabled="loading || !input.trim() || !isReady || !canSend">
            {{ loading ? "..." : "Send" }}
          </BaseButton>
          <BaseButton variant="ghost" size="sm" type="button" :disabled="loading" @click="clear">
            Clear
          </BaseButton>
        </div>
      </form>
    </Card>

    <Card v-else class="space-y-8">
      <section class="space-y-3">
        <h2 class="text-sm font-semibold text-surface-light uppercase tracking-wider">
          Current setup
        </h2>
        <p v-if="configLoading" class="text-surface-mid text-sm">Loading…</p>
        <dl v-else-if="chatConfig" class="grid gap-2 text-sm">
          <div class="flex gap-2">
            <dt class="text-surface-mid w-28 shrink-0">Provider</dt>
            <dd class="text-surface-light">{{ chatConfig.provider }}</dd>
          </div>
          <div class="flex gap-2">
            <dt class="text-surface-mid w-28 shrink-0">Model</dt>
            <dd class="text-surface-light font-mono text-xs">{{ chatConfig.model }}</dd>
          </div>
          <div class="flex gap-2">
            <dt class="text-surface-mid w-28 shrink-0">Base URL</dt>
            <dd class="text-surface-light font-mono text-xs break-all">
              {{ chatConfig.base_url ?? "Gemini API" }}
            </dd>
          </div>
          <div class="flex gap-2">
            <dt class="text-surface-mid w-28 shrink-0">API key</dt>
            <dd :class="chatConfig.configured ? 'text-status-success' : 'text-status-warning'">
              {{ chatConfig.configured ? "configured" : "missing" }}
            </dd>
          </div>
          <div class="flex gap-2">
            <dt class="text-surface-mid w-28 shrink-0">Enabled</dt>
            <dd class="text-surface-light">{{ chatConfig.enabled ? "yes" : "no" }}</dd>
          </div>
        </dl>
        <BaseButton variant="ghost" size="sm" :disabled="configLoading" @click="loadConfig">
          Refresh
        </BaseButton>
      </section>

      <section v-if="chatConfig?.configured" class="space-y-3">
        <h2 class="text-sm font-semibold text-surface-light uppercase tracking-wider">
          Troubleshooting
        </h2>
        <ul class="text-surface-mid text-sm leading-relaxed list-disc pl-5 space-y-2">
          <li>
            <strong class="text-surface-light font-medium">Quota or rate limit</strong> — wait for
            the retry window, then try again. Check RPM and daily (RPD) limits in
            <a
              class="text-accent-blue hover:text-accent-violet transition-colors"
              href="https://aistudio.google.com/"
              rel="noopener noreferrer"
              target="_blank"
            >
              Google AI Studio
            </a>
            (daily caps reset at midnight Pacific). Free-tier keys exhaust quickly during testing.
            Disable competing features in <code class="text-surface-sage">.env</code> while testing
            chat: <code class="text-surface-sage">AI_SEARCH_ENABLED=false</code>,
            <code class="text-surface-sage">TASK_INTAKE_AI_ENABLED=false</code>,
            <code class="text-surface-sage">NEWS_INGEST_ENABLED=false</code>.
          </li>
          <li>
            <strong class="text-surface-light font-medium">No sources / empty answers</strong> —
            backfill the search index with
            <code class="text-surface-sage">make reindex-search</code> (or
            <code class="text-surface-sage">python scripts/reindex_search.py</code> in the API
            container), then ask about indexed tasks, recipes, or expenses.
          </li>
          <li>
            <strong class="text-surface-light font-medium">App rate limit</strong> — this tool caps
            chat to 5 messages per 5 minutes per signed-in user.
          </li>
          <li>
            <strong class="text-surface-light font-medium">After .env changes</strong> — set
            <code class="text-surface-sage">GEMINI_API_KEY</code>,
            <code class="text-surface-sage">GEMINI_CHAT_MODEL</code>, and
            <code class="text-surface-sage">AI_CHAT_ENABLED=true</code>, then restart the backend.
          </li>
        </ul>
      </section>

      <section class="space-y-3">
        <h2 class="text-sm font-semibold text-surface-light uppercase tracking-wider">
          How it works
        </h2>
        <p class="text-surface-mid text-sm leading-relaxed">
          AI chat searches your indexed content first (portfolio, recipes, tasks, expenses, and
          more), then streams a grounded answer with citations. Set
          <code class="text-surface-sage">GEMINI_API_KEY</code> and
          <code class="text-surface-sage">GEMINI_CHAT_MODEL</code> in your server
          <code class="text-surface-sage">.env</code>, run
          <code class="text-surface-sage">python scripts/reindex_search.py</code> after deploy, then
          restart the backend. Set <code class="text-surface-sage">AI_CHAT_ENABLED=false</code>
          to hide this tool entirely.
        </p>
        <p class="text-surface-mid text-sm leading-relaxed">
          The same Gemini key is shared by AI chat, public search, news ingest, and task intake.
          Free-tier keys have low requests-per-minute limits. This app also caps chat to 5 messages
          per 5 minutes per IP.
        </p>
      </section>

      <section class="space-y-4">
        <h2 class="text-sm font-semibold text-surface-light uppercase tracking-wider">
          Example .env snippets
        </h2>
        <div
          v-for="example in PROVIDER_EXAMPLES"
          :key="example.name"
          class="rounded-lg border border-surface-border bg-surface-dark p-4 space-y-2"
        >
          <p class="text-sm text-surface-light font-medium">{{ example.name }}</p>
          <pre class="text-xs text-surface-sage whitespace-pre-wrap font-mono">{{
            example.env
          }}</pre>
        </div>
        <p class="text-surface-mid text-xs">
          Get a key from
          <a
            class="text-accent-blue hover:text-accent-violet transition-colors"
            href="https://ai.google.dev/gemini-api/docs"
            rel="noopener noreferrer"
            target="_blank"
          >
            Google AI Studio
          </a>
          and restart the backend after changing server env.
        </p>
      </section>
    </Card>
  </AdminPageLayout>
</template>
