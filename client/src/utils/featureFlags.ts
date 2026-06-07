/** Whether the AI chat tool is available in the admin UI. */
export function isAiChatEnabled(): boolean {
  return import.meta.env.VITE_AI_CHAT_ENABLED !== "false";
}

/** Whether the public portfolio AI search widget is available. */
export function isAiSearchEnabled(): boolean {
  return import.meta.env.VITE_AI_SEARCH_ENABLED !== "false";
}
