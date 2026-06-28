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

function requestStreamFlush(callback: () => void): number {
  return window.requestAnimationFrame
    ? window.requestAnimationFrame(callback)
    : window.setTimeout(callback, 16);
}

function cancelStreamFlush(id: number): void {
  if (window.cancelAnimationFrame) {
    window.cancelAnimationFrame(id);
    return;
  }
  window.clearTimeout(id);
}

function createStreamEventApplier(messages: ChatMessage[]): {
  apply: (events: StreamEvent[]) => void;
  flush: () => void;
} {
  let pendingDelta = "";
  let pendingSources: SearchSource[] | null = null;
  let flushId: number | null = null;

  function flush(): void {
    if (flushId !== null) {
      cancelStreamFlush(flushId);
      flushId = null;
    }

    if (!pendingDelta && !pendingSources) return;

    const last = messages.at(-1);
    if (!last || last.role !== "assistant") return;

    if (pendingSources) {
      last.sources = pendingSources;
      pendingSources = null;
    }
    if (pendingDelta) {
      last.content += pendingDelta;
      pendingDelta = "";
    }
  }

  function scheduleFlush(): void {
    if (flushId !== null) return;
    flushId = requestStreamFlush(flush);
  }

  function apply(events: StreamEvent[]): void {
    for (const event of events) {
      if (event.error) {
        throw new Error(event.error);
      }
      if (event.sources) {
        pendingSources = event.sources;
      }
      if (event.delta) {
        pendingDelta += event.delta;
      }
    }
    if (!pendingDelta && !pendingSources) return;
    scheduleFlush();
  }

  return { apply, flush };
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
      const streamEvents = createStreamEventApplier(messages.value);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const { events, rest } = parseSseEvents(buffer);
        buffer = rest;
        streamEvents.apply(events);
      }

      if (buffer.trim()) {
        const { events } = parseSseEvents(`${buffer}\n\n`);
        streamEvents.apply(events);
      }
      streamEvents.flush();
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
