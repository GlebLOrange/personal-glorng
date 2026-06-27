import { onUnmounted, ref } from "vue";

import { streamingPost, userSafeStreamError } from "@/composables/streamingPost";
import type { ChatMessage, SearchSource } from "@/types/search";

export type { ChatMessage, SearchSource };

interface StreamEvent {
  sources?: SearchSource[];
  delta?: string;
  done?: boolean;
  model?: string;
  error?: string;
}

export function parseSseEvents(buffer: string): { events: StreamEvent[]; rest: string } {
  const events: StreamEvent[] = [];
  const parts = buffer.split("\n\n");
  const rest = parts.pop() ?? "";

  for (const part of parts) {
    const line = part.split("\n").find((entry) => entry.startsWith("data: "));
    if (!line) continue;
    try {
      events.push(JSON.parse(line.slice(6)) as StreamEvent);
    } catch {
      // ignore malformed chunks
    }
  }

  return { events, rest };
}

function applyStreamEvents(messages: ChatMessage[], events: StreamEvent[]): void {
  for (const event of events) {
    if (event.error) {
      throw new Error(event.error);
    }
    const last = messages.at(-1);
    if (!last || last.role !== "assistant") continue;
    if (event.sources) {
      last.sources = event.sources;
    }
    if (event.delta) {
      last.content += event.delta;
    }
  }
}

function showAssistantError(messages: ChatMessage[], message: string): void {
  const content = `I couldn't get an AI response: ${message}`;
  const last = messages.at(-1);
  if (last?.role === "assistant") {
    last.content = content;
    return;
  }
  messages.push({ role: "assistant", content, sources: [] });
}

interface UseSearchChatOptions {
  endpoint: string;
  onError?: (message: string) => void;
  beforeSend?: () => boolean | Promise<boolean>;
}

export function useSearchChat(options: UseSearchChatOptions) {
  const messages = ref<ChatMessage[]>([]);
  const input = ref("");
  const loading = ref(false);
  const abortController = ref<AbortController | null>(null);

  onUnmounted(() => {
    abortController.value?.abort();
  });

  async function send(): Promise<void> {
    const text = input.value.trim();
    if (!text || loading.value) return;

    if (options.beforeSend) {
      const allowed = await options.beforeSend();
      if (!allowed) return;
    }

    messages.value.push({ role: "user", content: text });
    input.value = "";
    loading.value = true;
    messages.value.push({ role: "assistant", content: "", sources: [] });

    abortController.value?.abort();
    const controller = new AbortController();
    abortController.value = controller;

    try {
      const payload = messages.value
        .slice(0, -1)
        .map((message) => ({ role: message.role, content: message.content }));

      const response = await streamingPost(
        options.endpoint,
        { messages: payload },
        { signal: controller.signal },
      );

      if (!response.ok) {
        let detail: string | undefined;
        try {
          const body = (await response.json()) as { detail?: string };
          detail = body.detail;
        } catch {
          // ignore non-JSON error bodies
        }
        throw new Error(userSafeStreamError(response.status, detail));
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
        applyStreamEvents(messages.value, events);
      }

      if (buffer.trim()) {
        const { events } = parseSseEvents(`${buffer}\n\n`);
        applyStreamEvents(messages.value, events);
      }
    } catch (err) {
      if (controller.signal.aborted) {
        return;
      }
      const msg = err instanceof Error ? err.message : "Failed to get AI response";
      options.onError?.(msg);
      showAssistantError(messages.value, msg);
      throw err;
    } finally {
      loading.value = false;
      if (abortController.value === controller) {
        abortController.value = null;
      }
    }
  }

  function clear(): void {
    abortController.value?.abort();
    messages.value = [];
  }

  return {
    messages,
    input,
    loading,
    send,
    clear,
  };
}

/** Alias for streaming chat composable used by public and admin surfaces. */
export const useSseChat = useSearchChat;
