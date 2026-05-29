<script setup lang="ts">
import { nextTick, ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { useNotify } from "@/composables/useNotify";
import { useAuthStore } from "@/stores/auth";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface StreamEvent {
  delta?: string;
  done?: boolean;
  model?: string;
  error?: string;
}

const messages = ref<Message[]>([]);
const input = ref("");
const loading = ref(false);
const chatEnd = ref<HTMLElement | null>(null);
const { toast } = useNotify();

function scrollToBottom(): void {
  nextTick(() => chatEnd.value?.scrollIntoView({ behavior: "smooth" }));
}

function parseSseEvents(buffer: string): { events: StreamEvent[]; rest: string } {
  const events: StreamEvent[] = [];
  const parts = buffer.split("\n\n");
  const rest = parts.pop() ?? "";

  for (const part of parts) {
    const line = part
      .split("\n")
      .find((entry) => entry.startsWith("data: "));
    if (!line) continue;
    try {
      events.push(JSON.parse(line.slice(6)) as StreamEvent);
    } catch {
      // ignore malformed chunks
    }
  }

  return { events, rest };
}

async function send(): Promise<void> {
  const text = input.value.trim();
  if (!text || loading.value) return;

  const auth = useAuthStore();
  if (!auth.accessToken) {
    toast("Not authenticated", "error");
    return;
  }

  messages.value.push({ role: "user", content: text });
  input.value = "";
  loading.value = true;
  messages.value.push({ role: "assistant", content: "" });
  scrollToBottom();

  try {
    const payload = messages.value
      .slice(0, -1)
      .map((m) => ({ role: m.role, content: m.content }));

    const response = await fetch("/api/tools/ai-chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.accessToken}`,
      },
      body: JSON.stringify({ messages: payload }),
    });

    if (!response.ok) {
      let detail = "Failed to get AI response";
      try {
        const body = (await response.json()) as { detail?: string };
        detail = body.detail ?? detail;
      } catch {
        // ignore non-JSON error bodies
      }
      throw new Error(detail);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("Streaming not supported");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const { events, rest } = parseSseEvents(buffer);
      buffer = rest;

      for (const event of events) {
        if (event.error) {
          throw new Error(event.error);
        }
        if (event.delta) {
          const last = messages.value.at(-1);
          if (last?.role === "assistant") {
            last.content += event.delta;
          }
        }
      }
      scrollToBottom();
    }
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Failed to get AI response";
    toast(msg, "error");
    messages.value.pop();
    if (messages.value.at(-1)?.role === "user") {
      messages.value.pop();
    }
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
        <span class="text-surface-mid font-mono text-xs uppercase tracking-wider">openai</span>
      </div>

      <div class="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
        <p v-if="!messages.length" class="text-surface-mid text-sm text-center mt-8">
          Start a conversation.
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
          {{ msg.content }}<span
            v-if="loading && msg.role === 'assistant' && i === messages.length - 1"
            class="inline-block w-2 h-4 ml-0.5 bg-accent-violet/60 animate-pulse align-middle"
          />
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
          <BaseButton variant="primary" :disabled="loading || !input.trim()">
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
