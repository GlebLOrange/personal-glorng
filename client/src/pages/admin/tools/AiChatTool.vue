<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef } from "vue";

import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import QuestionIcon from "@/components/icons/QuestionIcon.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import SearchChatMessages from "@/components/search/SearchChatMessages.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { Card } from "@/components/ui/card";
import { ACTION_PILL_BASE, iconActionClass } from "@/constants/httpStatusColors";
import { TOOLBAR_POPOVER_PANEL_CHROME_CLASS } from "@/constants/toolbarPopover";
import { useChatConfig } from "@/composables/useChatConfig";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import { useSearchChat } from "@/composables/useSearchChat";
import { useAuthStore } from "@/stores/auth";
import type { AdminChatConfig } from "@/types/search";

const AI_CHAT_TABS = [{ id: "chat", label: "chat" }] as const;

const PROVIDER_EXAMPLES = [
  {
    name: "Groq",
    env: `GROQ_API_KEY=gsk_...
GROQ_CHAT_MODEL=llama-3.3-70b-versatile`,
  },
] as const;

const activeTab = ref("chat");
const chatEnd = ref<HTMLElement | null>(null);
const helpOpen = ref(false);
const helpRootRef = useTemplateRef<HTMLElement>("helpRoot");
let helpCloseTimer: ReturnType<typeof setTimeout> | null = null;

const { toast } = useNotify();
const { isSuperuser } = usePermissions();
const canSend = computed(() => isSuperuser.value);

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
      toast("Superuser access required", "error");
      return false;
    }
    if (!isReady.value) {
      toast("AI chat is not configured — open setup help", "error");
      return false;
    }
    return true;
  },
});

const providerLabel = computed(() => chatConfig.value?.provider ?? "…");
const modelLabel = computed(() => chatConfig.value?.model ?? "…");
const helpButtonClass = computed(() => iconActionClass("1xx", helpOpen.value));

function clearHelpCloseTimer(): void {
  if (helpCloseTimer !== null) {
    clearTimeout(helpCloseTimer);
    helpCloseTimer = null;
  }
}

function showHelp(): void {
  clearHelpCloseTimer();
  helpOpen.value = true;
}

function scheduleHideHelp(): void {
  clearHelpCloseTimer();
  helpCloseTimer = setTimeout(() => {
    helpOpen.value = false;
    helpCloseTimer = null;
  }, 120);
}

function hideHelp(): void {
  clearHelpCloseTimer();
  helpOpen.value = false;
}

function toggleHelp(): void {
  clearHelpCloseTimer();
  helpOpen.value = !helpOpen.value;
}

function onDocumentPointerDown(event: PointerEvent): void {
  if (!helpOpen.value) return;
  const root = helpRootRef.value;
  if (!root) return;
  if (event.target instanceof Node && root.contains(event.target)) return;
  hideHelp();
}

function onDocumentKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape" && helpOpen.value) {
    event.stopPropagation();
    hideHelp();
  }
}

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
  document.addEventListener("pointerdown", onDocumentPointerDown, true);
  document.addEventListener("keydown", onDocumentKeydown, true);
  void loadConfig().then(() => {
    if (chatConfig.value && !chatConfig.value.configured) {
      toast("AI chat is not configured — open setup help", "error");
    }
  });
});

onBeforeUnmount(() => {
  clearHelpCloseTimer();
  document.removeEventListener("pointerdown", onDocumentPointerDown, true);
  document.removeEventListener("keydown", onDocumentKeydown, true);
});
</script>

<template>
  <AdminPageLayout title="ai chat" back-to="/admin">
    <AdminTabBar v-model="activeTab" :tabs="[...AI_CHAT_TABS]" aria-label="ai chat sections">
      <template #end>
        <div
          ref="helpRoot"
          class="relative"
          @mouseenter="showHelp"
          @mouseleave="scheduleHideHelp"
        >
          <button
            type="button"
            :class="helpButtonClass"
            aria-label="setup help"
            :aria-expanded="helpOpen"
            aria-controls="ai-chat-setup-help"
            @click.stop="toggleHelp"
            @focus="showHelp"
            @blur="scheduleHideHelp"
          >
            <QuestionIcon class-name="size-3.5" />
          </button>
          <div
            id="ai-chat-setup-help"
            role="tooltip"
            class="scrollbar-thin absolute right-0 top-full z-30 mt-1 w-[min(100vw-2rem,28rem)] max-h-[min(50vh,24rem)] overflow-y-auto overscroll-contain text-left"
            :class="[TOOLBAR_POPOVER_PANEL_CHROME_CLASS, helpOpen ? undefined : 'sr-only']"
            @mouseenter="showHelp"
            @mouseleave="scheduleHideHelp"
          >
            <div class="space-y-3">
              <section class="space-y-2">
                <div class="flex items-center justify-between gap-3">
                  <h2 class="text-sm font-semibold lowercase text-surface-light">current setup</h2>
                  <button
                    type="button"
                    :class="[
                      ACTION_PILL_BASE,
                      'gap-1.5 shrink-0 border-transparent bg-accent-blue/3 text-accent-blue hover:enabled:border-accent-blue/40 hover:enabled:bg-accent-blue/15',
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
                  class="flex cursor-pointer list-none items-center gap-1.5 px-2 py-1.5 text-sm font-semibold lowercase text-surface-light [&::-webkit-details-marker]:hidden"
                >
                  <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
                  troubleshooting
                </summary>
                <ul class="list-disc space-y-2 border-t border-surface-border/60 px-2 py-2 pl-7 text-xs leading-relaxed text-surface-mid">
                  <li>
                    <strong class="font-medium text-surface-light">Quota or rate limit</strong> —
                    wait for the retry window, then try again. Check RPM limits in
                    <a
                      class="text-accent-blue transition-colors hover:text-accent-blue/80"
                      href="https://console.groq.com/"
                      rel="noopener noreferrer"
                      target="_blank"
                    >
                      Groq Console
                    </a>
                    . Disable competing features in <code class="text-surface-sage">.env</code> while
                    testing chat:
                    <code class="text-surface-sage">TASK_INTAKE_AI_ENABLED=false</code>,
                    <code class="text-surface-sage">NEWS_INGEST_ENABLED=false</code>
                  </li>
                  <li>
                    <strong class="font-medium text-surface-light">App rate limit</strong> — this tool
                    caps chat to 5 messages per 5 minutes per signed-in superuser
                  </li>
                  <li>
                    <strong class="font-medium text-surface-light">After .env changes</strong> — set
                    <code class="text-surface-sage">GROQ_API_KEY</code>,
                    <code class="text-surface-sage">GROQ_CHAT_MODEL</code>, and
                    <code class="text-surface-sage">AI_CHAT_ENABLED=true</code>, then restart the
                    backend
                  </li>
                </ul>
              </details>

              <details class="group rounded-md border border-surface-border/60 open:border-surface-border">
                <summary
                  class="flex cursor-pointer list-none items-center gap-1.5 px-2 py-1.5 text-sm font-semibold lowercase text-surface-light [&::-webkit-details-marker]:hidden"
                >
                  <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
                  how it works
                </summary>
                <div class="space-y-2 border-t border-surface-border/60 px-2 py-2 text-xs leading-relaxed text-surface-mid">
                  <p>
                    Superuser-only plain LLM chat. Set
                    <code class="text-surface-sage">GROQ_API_KEY</code> and
                    <code class="text-surface-sage">GROQ_CHAT_MODEL</code> in your server
                    <code class="text-surface-sage">.env</code>, then restart the backend. Set
                    <code class="text-surface-sage">AI_CHAT_ENABLED=false</code> to hide this tool
                    entirely
                  </p>
                  <p>
                    The same Groq key is shared by AI chat, news ingest, and task intake. Groq
                    enforces per-model RPM limits. This app also caps chat to 5 messages per 5
                    minutes per superuser
                  </p>
                </div>
              </details>

              <details class="group rounded-md border border-surface-border/60 open:border-surface-border">
                <summary
                  class="flex cursor-pointer list-none items-center gap-1.5 px-2 py-1.5 text-sm font-semibold lowercase text-surface-light [&::-webkit-details-marker]:hidden"
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
                      class="text-accent-blue transition-colors hover:text-accent-blue/80"
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
            </div>
          </div>
        </div>
      </template>
    </AdminTabBar>

    <Card class="flex h-[65vh] flex-col">
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
          user-class="bg-accent-blue/10 border border-accent-blue/20 text-surface-light ml-8"
          assistant-class="bg-surface-dark border border-surface-border text-surface-sage mr-8"
        >
          <template #end>
            <div ref="chatEnd" />
          </template>
        </SearchChatMessages>
      </div>

      <form
        class="flex items-stretch gap-3 border-t border-surface-border pt-4"
        @submit.prevent="handleSend"
      >
        <!-- Match clear + send stack: h-10 + gap-2 + h-10 -->
        <BaseTextarea
          v-model="input"
          class="min-w-0 flex-1 [&>div]:box-border [&>div]:min-h-[calc(2.5rem+0.5rem+2.5rem)] [&>div]:items-stretch [&_textarea]:h-full [&_textarea]:min-h-full [&_textarea]:resize-none"
          rows="3"
          placeholder="message the assistant…"
          aria-label="message"
          @keydown.enter.exact.prevent="handleSend"
        />
        <div class="flex flex-col gap-2">
          <ToolbarPillButton family="4xx" type="button" :disabled="loading" @click="clear">
            clear
          </ToolbarPillButton>
          <ToolbarPillButton
            family="2xx"
            type="submit"
            :disabled="loading || !input.trim() || !isReady || !canSend"
          >
            {{ loading ? "…" : "send" }}
          </ToolbarPillButton>
        </div>
      </form>
    </Card>
  </AdminPageLayout>
</template>
