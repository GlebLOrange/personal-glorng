<script setup lang="ts">
import { nextTick, onMounted, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ProviderInfo {
  id: string;
  models: string[];
  default_model: string;
}

interface ChatApiResponse {
  reply: string;
  model: string;
  usage: { prompt_tokens: number; completion_tokens: number; total_tokens: number };
}

const PROVIDER = "groq";

const messages = ref<Message[]>([]);
const input = ref("");
const loading = ref(false);
const chatEnd = ref<HTMLElement | null>(null);
const { toast } = useNotify();

const models = ref<string[]>([]);
const selectedModel = ref("");

async function loadProviders(): Promise<void> {
  try {
    const { data } = await api.get<ProviderInfo[]>("/tools/ai-chat/providers");
    const groq = data.find((p) => p.id === PROVIDER);
    if (!groq) {
      toast("Groq API key is not configured", "error");
      return;
    }
    models.value = groq.models;
    selectedModel.value = groq.default_model;
  } catch {
    toast("Failed to load AI models", "error");
  }
}

onMounted(loadProviders);

function scrollToBottom(): void {
  nextTick(() => chatEnd.value?.scrollIntoView({ behavior: "smooth" }));
}

async function send(): Promise<void> {
  const text = input.value.trim();
  if (!text || loading.value || !selectedModel.value) return;

  messages.value.push({ role: "user", content: text });
  input.value = "";
  loading.value = true;
  scrollToBottom();

  try {
    const payload = messages.value.map((m) => ({ role: m.role, content: m.content }));
    const { data } = await api.post<ChatApiResponse>("/tools/ai-chat", {
      messages: payload,
      provider: PROVIDER,
      model: selectedModel.value,
    });
    messages.value.push({ role: "assistant", content: data.reply });
  } catch (err) {
    const msg =
      (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
      "Failed to get AI response";
    toast(msg, "error");
    messages.value.pop();
  } finally {
    loading.value = false;
    scrollToBottom();
  }
}

function clear(): void {
  messages.value = [];
}
</script>

<template>
  <AdminPageLayout title="ai chat">
    <BaseCard class="flex flex-col h-[65vh]">
      <div class="flex items-center gap-3 mb-4 pb-4 border-b border-surface-border">
        <span class="text-surface-mid font-mono text-xs uppercase tracking-wider">groq</span>

        <select
          v-model="selectedModel"
          class="bg-surface-dark border border-surface-border rounded-lg px-3 py-1.5
                 text-surface-light font-mono text-xs focus:outline-none focus:border-accent-blue
                 transition-colors appearance-none cursor-pointer"
        >
          <option v-for="m in models" :key="m" :value="m">
            {{ m }}
          </option>
        </select>
      </div>

      <div class="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
        <p v-if="!messages.length" class="text-surface-mid text-sm text-center mt-8">
          Start a conversation — pick a model above.
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
          <span class="text-[10px] uppercase tracking-wider block mb-1"
            :class="msg.role === 'user' ? 'text-accent-blue' : 'text-accent-violet'"
          >
            {{ msg.role }}
          </span>
          {{ msg.content }}
        </div>

        <div v-if="loading" class="bg-surface-dark border border-surface-border rounded-lg px-4 py-3 mr-8">
          <span class="text-[10px] uppercase tracking-wider text-accent-violet block mb-1">assistant</span>
          <span class="text-surface-mid text-sm animate-pulse">thinking...</span>
        </div>

        <div ref="chatEnd" />
      </div>

      <form class="flex gap-3 border-t border-surface-border pt-4" @submit.prevent="send">
        <textarea
          v-model="input"
          rows="2"
          placeholder="Ask anything..."
          class="flex-1 bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light
                 font-mono text-sm focus:outline-none focus:border-accent-blue transition-colors
                 placeholder:text-surface-mid/50 resize-none"
          @keydown.enter.exact.prevent="send"
        />
        <div class="flex flex-col gap-2">
          <BaseButton variant="primary" :disabled="loading || !input.trim() || !selectedModel">
            {{ loading ? "..." : "Send" }}
          </BaseButton>
          <BaseButton variant="ghost" size="sm" type="button" :disabled="loading" @click="clear">
            Clear
          </BaseButton>
        </div>
      </form>
    </BaseCard>
  </AdminPageLayout>
</template>
