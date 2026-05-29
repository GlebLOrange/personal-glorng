/** Whether the AI chat tool is available in the admin UI. */
export function isAiChatEnabled(): boolean {
  return import.meta.env.VITE_AI_CHAT_ENABLED !== "false";
}
