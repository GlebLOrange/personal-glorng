import { ref } from "vue";

export interface SearchSource {
  id: number;
  title: string;
  url: string;
  source_type: string;
  snippet: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SearchSource[];
}

let messageCounter = 0;

function nextMessageId(): string {
  messageCounter += 1;
  return `msg-${messageCounter}-${Date.now()}`;
}

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

interface UseSearchChatOptions {
  endpoint: string;
  onError?: (message: string) => void;
}

export function useSearchChat(options: UseSearchChatOptions) {
  const messages = ref<ChatMessage[]>([]);
  const input = ref("");
  const loading = ref(false);

  async function send(): Promise<void> {
    const text = input.value.trim();
    if (!text || loading.value) return;

    messages.value.push({ id: nextMessageId(), role: "user", content: text });
    input.value = "";
    loading.value = true;
    messages.value.push({
      id: nextMessageId(),
      role: "assistant",
      content: "",
      sources: [],
    });

    try {
      const payload = messages.value
        .slice(0, -1)
        .map((message) => ({ role: message.role, content: message.content }));

      const response = await fetch(options.endpoint, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
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
          const last = messages.value.at(-1);
          if (!last || last.role !== "assistant") continue;
          if (event.sources) {
            last.sources = event.sources;
          }
          if (event.delta) {
            last.content += event.delta;
          }
        }
      }

      if (buffer.trim()) {
        const { events } = parseSseEvents(`${buffer}\n\n`);
        for (const event of events) {
          if (event.error) {
            throw new Error(event.error);
          }
          const last = messages.value.at(-1);
          if (!last || last.role !== "assistant") continue;
          if (event.sources) {
            last.sources = event.sources;
          }
          if (event.delta) {
            last.content += event.delta;
          }
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to get AI response";
      options.onError?.(msg);
      messages.value.pop();
      if (messages.value.at(-1)?.role === "user") {
        messages.value.pop();
      }
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function clear(): void {
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
