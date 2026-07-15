export interface SearchSource {
  id: number;
  title: string;
  url: string;
  source_type: string;
  snippet: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: SearchSource[];
  error?: boolean;
}

export interface BaseChatConfig {
  enabled: boolean;
  configured: boolean;
}

export type SearchConfig = BaseChatConfig;

export interface AdminChatConfig extends BaseChatConfig {
  model: string;
  provider: string;
  base_url: string | null;
}
