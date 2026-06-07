<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";

import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { useSearchChat } from "@/composables/useSearchChat";
import { useAuthStore } from "@/stores/auth";
import { getApiErrorMessage } from "@/types/api";
import { isExternalHref, safeNavigationHref } from "@/utils/safeUrl";

type AiChatTab = "chat" | "settings";

interface ChatConfig {
  enabled: boolean;
  configured: boolean;
  model: string;
  provider: string;
  base_url: string | null;
}

const AI_CHAT_TABS = [
  { id: "chat", label: "chat" },
  { id: "settings", label: "settings" },
] as const;

const PROVIDER_EXAMPLES = [
  {
    name: "Groq (free tier)",
    env: `OPENAI_API_KEY=gsk_...
LLM_BASE_URL=https://api.groq.com/openai/v1
OPENAI_CHAT_MODEL=llama-3.3-70b-versatile`,
  },
  {
    name: "Ollama (local, free)",
    env: `OPENAI_API_KEY=ollama
LLM_BASE_URL=http://host.docker.internal:11434/v1
OPENAI_CHAT_MODEL=llama3.2`,
  },
  {
    name: "OpenRouter (some free models)",
    env: `OPENAI_API_KEY=sk-or-...
LLM_BASE_URL=https://openrouter.ai/api/v1
OPENAI_CHAT_MODEL=google/gemma-2-9b-it:free`,
  },
] as const;

const activeTab = ref<AiChatTab>("chat");
const chatConfig = ref<ChatConfig | null>(null);
const configLoading = ref(true);
const chatEnd = ref<HTMLElement | null>(null);
const { toast } = useNotify();

const { messages, input, loading, send, clear } = useSearchChat({
  endpoint: "/api/tools/ai-chat",
  onError: (message) => toast(message, "error"),
});

const providerLabel = computed(() => chatConfig.value?.provider ?? "…");
const modelLabel = computed(() => chatConfig.value?.model ?? "…");
const isReady = computed(() => Boolean(chatConfig.value?.enabled && chatConfig.value?.configured));


interface SourceLink {
  href: string;
  external: boolean;
}

function sourceLink(url: string): SourceLink | null {
  const href = safeNavigationHref(url);
  if (!href) {
    return null;
  }
  return { href, external: isExternalHref(href) };
}

function scrollToBottom(): void {
  nextTick(() => chatEnd.value?.scrollIntoView({ behavior: "smooth" }));
}

async function loadConfig(): Promise<void> {
  configLoading.value = true;
  try {
    const { data } = await api.get<ChatConfig>("/tools/ai-chat/config");
    chatConfig.value = data;
  } catch (err) {
    toast(getApiErrorMessage(err, "Failed to load AI chat config"), "error");
  } finally {
    configLoading.value = false;
  }
}

async function handleSend(): Promise<void> {
  const auth = useAuthStore();
  if (!auth.isAuthenticated) {
    toast("Not authenticated", "error");
    return;
  }

  if (!isReady.value) {
    toast("AI chat is not configured — check Settings", "error");
    activeTab.value = "settings";
    return;
  }

  try {
    await send();
    scrollToBottom();
  } catch {
    // toast handled in composable
  }
}

onMounted(() => {
  void loadConfig();
});
</script>

<template>
  <AdminPageLayout title="ai chat">
    <AdminTabBar v-model="activeTab" :tabs="[...AI_CHAT_TABS]" />

    <BaseCard v-if="activeTab === 'chat'" class="flex flex-col h-[65vh]">
      <div class="flex items-center gap-3 mb-4 pb-4 border-b border-surface-border">
        <span class="text-surface-mid text-xs uppercase tracking-wider">
          {{ providerLabel }}
        </span>
        <span class="text-surface-mid/60 text-xs">·</span>
        <span class="text-surface-mid text-xs">{{ modelLabel }}</span>
        <span class="text-surface-mid/60 text-xs">· personal search</span>
        <span v-if="!configLoading && !isReady" class="ml-auto text-xs text-amber-400/90">
          not configured
        </span>
      </div>

      <div class="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
        <p v-if="!messages.length" class="text-surface-mid text-sm text-center mt-8">
          Search your indexed content — tasks, recipes, expenses, and more.
        </p>

        <div
          v-for="(msg, i) in messages"
          :key="i"
          :class="[
            'px-4 py-3 rounded-lg text-sm whitespace-pre-wrap leading-relaxed',
            msg.role === 'user'
              ? 'bg-accent-blue/10 border border-accent-blue/20 text-surface-light ml-8'
              : 'bg-surface-dark border border-surface-border text-surface-sage mr-8',
          ]"
        >
          <span
            class="text-[10px] uppercase tracking-wider block mb-1"
            :class="msg.role === 'user' ? 'text-accent-blue' : 'text-accent-violet'"
          >
            {{ msg.role }}
          </span>
          {{ msg.content
          }}<span
            v-if="loading && msg.role === 'assistant' && i === messages.length - 1"
            class="inline-block w-2 h-4 ml-0.5 bg-accent-violet/60 animate-pulse align-middle"
          />

          <div
            v-if="msg.role === 'assistant' && msg.sources?.length"
            class="mt-3 pt-3 border-t border-surface-border/70 space-y-2"
          >
            <p class="text-[10px] uppercase tracking-wider text-surface-mid">
              Searching your indexed content
            </p>
            <template v-for="source in msg.sources" :key="source.id">
              <a
                v-if="sourceLink(source.url)"
                :href="sourceLink(source.url)!.href"
                :rel="sourceLink(source.url)!.external ? 'noopener noreferrer' : undefined"
                :target="sourceLink(source.url)!.external ? '_blank' : undefined"
                class="block rounded-md border border-surface-border/80 bg-surface-card/60 px-3 py-2 hover:border-accent-violet/40 transition-colors"
              >
                <span class="text-xs text-accent-violet font-medium">{{ source.title }}</span>
                <span class="text-[10px] text-surface-mid block">{{ source.source_type }}</span>
                <span class="text-[11px] text-surface-mid line-clamp-2">{{ source.snippet }}</span>
              </a>
              <div
                v-else
                class="block rounded-md border border-surface-border/80 bg-surface-card/60 px-3 py-2"
              >
                <span class="text-xs text-accent-violet font-medium">{{ source.title }}</span>
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

        <div ref="chatEnd" />
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
          <BaseButton variant="primary" :disabled="loading || !input.trim() || !isReady">
            {{ loading ? "..." : "Send" }}
          </BaseButton>
          <BaseButton variant="ghost" size="sm" type="button" :disabled="loading" @click="clear">
            Clear
          </BaseButton>
        </div>
      </form>
    </BaseCard>

    <BaseCard v-else class="space-y-8">
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
              {{ chatConfig.base_url ?? "OpenAI default" }}
            </dd>
          </div>
          <div class="flex gap-2">
            <dt class="text-surface-mid w-28 shrink-0">API key</dt>
            <dd :class="chatConfig.configured ? 'text-emerald-400' : 'text-amber-400'">
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

      <section class="space-y-3">
        <h2 class="text-sm font-semibold text-surface-light uppercase tracking-wider">
          How it works
        </h2>
        <p class="text-surface-mid text-sm leading-relaxed">
          AI chat searches your indexed content first (portfolio, recipes, tasks, expenses, and
          more), then streams a grounded answer with citations. Set
          <code class="text-surface-sage">OPENAI_API_KEY</code>, optional
          <code class="text-surface-sage">LLM_BASE_URL</code>, and
          <code class="text-surface-sage">OPENAI_CHAT_MODEL</code> in your server
          <code class="text-surface-sage">.env</code>, run
          <code class="text-surface-sage">python scripts/reindex_search.py</code> after deploy, then
          restart the backend. Set <code class="text-surface-sage">AI_CHAT_ENABLED=false</code>
          to hide this tool entirely.
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
          For Ollama in Docker: run
          <code class="text-surface-sage">ollama pull &lt;model&gt;</code> on the host and use
          <code class="text-surface-sage">host.docker.internal</code> as shown above.
        </p>
      </section>
    </BaseCard>
  </AdminPageLayout>
</template>
