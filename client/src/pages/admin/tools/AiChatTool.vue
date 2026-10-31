<script setup lang="ts">
import { ref } from "vue";

import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import PageShell from "@/components/layout/PageShell.vue";
import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import SearchChatMessages from "@/components/search/SearchChatMessages.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { Card } from "@/components/ui/card";
import { ACTION_PILL_BASE } from "@/constants/httpStatusColors";
import { useAiChat } from "@/composables/useAiChat";

const AI_CHAT_TABS = [
  { id: "chat", label: "chat", icon: "queue" as const },
  { id: "settings", label: "settings", icon: "sync" as const },
] as const;

const PROVIDER_EXAMPLES = [
  {
    name: "Groq",
    env: `GROQ_API_KEY=gsk_...
GROQ_CHAT_MODEL=openai/gpt-oss-120b`,
  },
] as const;

const activeTab = ref("chat");
const chatEnd = ref<HTMLElement | null>(null);

const {
  chatConfig,
  configLoading,
  loadConfig,
  isReady,
  canSend,
  providerLabel,
  modelLabel,
  messages,
  input,
  loading,
  clear,
  handleSend,
} = useAiChat(chatEnd);
</script>

<template>
  <PageShell
    title="ai chat"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'ai chat' }]"
    back-to="/tools"
    max-width="5xl"
    :narrow="false"
    tool
  >
    <div class="page-tool-actions">
      <AdminTabBar
        v-model="activeTab"
        panel-id-prefix="ai-chat"
        :tabs="[...AI_CHAT_TABS]"
        aria-label="ai chat sections"
      />
    </div>

    <Card
      v-if="activeTab === 'chat'"
      id="ai-chat-panel-chat"
      role="tabpanel"
      aria-labelledby="ai-chat-tab-chat"
      class="flex h-[65vh] flex-col"
    >
      <div class="mb-4 flex items-center gap-3 border-b border-surface-border pb-4">
        <span class="text-xs text-surface-mid">
          {{ providerLabel }}
        </span>
        <span class="text-xs text-surface-mid/60">·</span>
        <span class="text-xs text-surface-mid">{{ modelLabel }}</span>
        <span v-if="!configLoading && !isReady" class="ml-auto text-xs text-status-warning/90">
          not configured
        </span>
        <span v-else-if="!canSend" class="ml-auto text-xs text-status-warning/90">
          superuser only
        </span>
      </div>

      <div class="mb-4 flex-1 overflow-y-auto pr-1">
        <SearchChatMessages
          :messages="messages"
          :loading="loading"
          show-role-labels
          empty-message="ask anything — responses stream from the configured Groq model"
          user-class="bg-accent-coral/10 border border-accent-coral/20 text-surface-light ml-8"
          assistant-class="bg-surface-dark border border-surface-border text-surface-sage mr-8"
        >
          <template #end>
            <div ref="chatEnd" />
          </template>
        </SearchChatMessages>
      </div>

      <div class="page-tool-actions mb-0 border-t border-surface-border pt-4">
        <form class="flex w-fit max-w-full items-stretch gap-3" @submit.prevent="handleSend">
          <!-- Match clear + send stack: h-10 + gap-2 + h-10 -->
          <BaseTextarea
            v-model="input"
            class="min-w-0 [&>div]:box-border [&>div]:min-h-[calc(2.5rem+0.5rem+2.5rem)] [&>div]:items-stretch [&_textarea]:h-full [&_textarea]:min-h-full [&_textarea]:resize-none"
            :rows="3"
            auto-width
            label="message"
            tip="message the assistant…"
            @keydown.enter.exact.prevent="handleSend"
          />
          <div class="flex flex-col gap-2">
            <ToolbarPillButton
              action="delete"
              type="button"
              class="w-auto"
              :disabled="loading"
              @click="clear"
            >
              clear
            </ToolbarPillButton>
            <ToolbarPillButton
              action="save"
              type="submit"
              class="w-auto"
              :disabled="loading || !input.trim() || !isReady || !canSend"
            >
              {{ loading ? "…" : "send" }}
            </ToolbarPillButton>
          </div>
        </form>
      </div>
    </Card>

    <Card
      v-else-if="activeTab === 'settings'"
      id="ai-chat-panel-settings"
      role="tabpanel"
      aria-labelledby="ai-chat-tab-settings"
      class="space-y-4 p-4"
    >
      <section class="space-y-2">
        <div class="flex items-center justify-between gap-3">
          <h2 class="text-sm font-semibold lowercase text-surface-light">current setup</h2>
          <button
            type="button"
            :class="[
              ACTION_PILL_BASE,
              'min-h-11 gap-1.5 shrink-0 border-transparent bg-accent-coral/3 text-accent-coral hover:enabled:border-accent-coral/40 hover:enabled:bg-accent-coral/15',
            ]"
            :disabled="configLoading"
            @click="loadConfig"
          >
            <RefreshIcon class-name="size-3.5 shrink-0" />
            refresh
          </button>
        </div>
        <p v-if="configLoading" class="text-sm lowercase text-surface-mid">loading…</p>
        <dl v-else-if="chatConfig" class="grid gap-1.5 text-sm">
          <div class="flex gap-2">
            <dt class="w-28 shrink-0 lowercase text-surface-mid">provider</dt>
            <dd class="text-surface-light">{{ chatConfig.provider }}</dd>
          </div>
          <div class="flex gap-2">
            <dt class="w-28 shrink-0 lowercase text-surface-mid">model</dt>
            <dd class="font-data text-xs text-surface-light">{{ chatConfig.model }}</dd>
          </div>
          <div class="flex gap-2">
            <dt class="w-28 shrink-0 lowercase text-surface-mid">base url</dt>
            <dd class="break-all font-data text-xs text-surface-light">
              {{ chatConfig.base_url ?? "Groq API" }}
            </dd>
          </div>
          <div class="flex gap-2">
            <dt class="w-28 shrink-0 lowercase text-surface-mid">api key</dt>
            <dd
              class="lowercase"
              :class="chatConfig.configured ? 'text-status-success' : 'text-status-warning'"
            >
              {{ chatConfig.configured ? "configured" : "missing" }}
            </dd>
          </div>
          <div class="flex gap-2">
            <dt class="w-28 shrink-0 lowercase text-surface-mid">enabled</dt>
            <dd class="lowercase text-surface-light">
              {{ chatConfig.enabled ? "yes" : "no" }}
            </dd>
          </div>
        </dl>
      </section>

      <details
        v-if="chatConfig?.configured"
        class="group rounded-md border border-surface-border/60 open:border-surface-border"
      >
        <summary
          class="flex min-h-11 cursor-pointer list-none items-center gap-1.5 px-2 py-1.5 text-sm font-semibold lowercase text-surface-light [&::-webkit-details-marker]:hidden"
        >
          <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
          troubleshooting
        </summary>
        <ul
          class="list-disc space-y-2 border-t border-surface-border/60 px-2 py-2 pl-7 text-xs leading-relaxed text-surface-mid"
        >
          <li>
            <strong class="font-medium text-surface-light">Quota or rate limit</strong> — wait for
            the retry window, then try again. Check RPM limits in
            <a
              class="text-accent-coral transition-colors hover:text-accent-coral/80"
              href="https://console.groq.com/"
              rel="noopener noreferrer"
              target="_blank"
            >
              Groq Console
            </a>
            . Disable competing features in
            <code class="text-surface-sage">.env</code> while testing chat:
            <code class="text-surface-sage">TASK_INTAKE_AI_ENABLED=false</code>,
            <code class="text-surface-sage">NEWS_INGEST_ENABLED=false</code>
          </li>
          <li>
            <strong class="font-medium text-surface-light">App rate limit</strong> — this tool caps
            chat to 5 messages per 5 minutes per signed-in superuser
          </li>
          <li>
            <strong class="font-medium text-surface-light">After .env changes</strong> — set
            <code class="text-surface-sage">GROQ_API_KEY</code>,
            <code class="text-surface-sage">GROQ_CHAT_MODEL</code>, and
            <code class="text-surface-sage">AI_CHAT_ENABLED=true</code>, then restart the backend
          </li>
        </ul>
      </details>

      <details class="group rounded-md border border-surface-border/60 open:border-surface-border">
        <summary
          class="flex min-h-11 cursor-pointer list-none items-center gap-1.5 px-2 py-1.5 text-sm font-semibold lowercase text-surface-light [&::-webkit-details-marker]:hidden"
        >
          <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
          how it works
        </summary>
        <div
          class="space-y-2 border-t border-surface-border/60 px-2 py-2 text-xs leading-relaxed text-surface-mid"
        >
          <p>
            Superuser-only plain LLM chat. Set
            <code class="text-surface-sage">GROQ_API_KEY</code> and
            <code class="text-surface-sage">GROQ_CHAT_MODEL</code> in your server
            <code class="text-surface-sage">.env</code>, then restart the backend. Set
            <code class="text-surface-sage">AI_CHAT_ENABLED=false</code> to hide this tool entirely
          </p>
          <p>
            The same Groq key is shared by AI chat, news ingest, and task intake. Groq enforces
            per-model RPM limits. This app also caps chat to 5 messages per 5 minutes per superuser
          </p>
        </div>
      </details>

      <details class="group rounded-md border border-surface-border/60 open:border-surface-border">
        <summary
          class="flex min-h-11 cursor-pointer list-none items-center gap-1.5 px-2 py-1.5 text-sm font-semibold lowercase text-surface-light [&::-webkit-details-marker]:hidden"
        >
          <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
          example .env snippets
        </summary>
        <div class="space-y-3 border-t border-surface-border/60 px-2 py-2">
          <div
            v-for="example in PROVIDER_EXAMPLES"
            :key="example.name"
            class="space-y-2 rounded-lg border border-surface-border bg-surface-dark p-2.5"
          >
            <p class="text-xs font-medium text-surface-light">{{ example.name }}</p>
            <pre class="whitespace-pre-wrap font-data text-xs text-surface-sage">{{
              example.env
            }}</pre>
          </div>
          <p class="text-xs text-surface-mid">
            Get a key from
            <a
              class="text-accent-coral transition-colors hover:text-accent-coral/80"
              href="https://console.groq.com/keys"
              rel="noopener noreferrer"
              target="_blank"
            >
              Groq Console
            </a>
            and restart the backend after changing server env
          </p>
        </div>
      </details>
    </Card>
  </PageShell>
</template>
