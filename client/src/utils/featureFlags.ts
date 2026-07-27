/** Whether the AI chat tool is available in the admin UI. */
export function isAiChatEnabled(): boolean {
  return import.meta.env.VITE_AI_CHAT_ENABLED !== "false";
}

/** Whether expenses ledger and public calculator are available (opt-in). */
export function isExpensesEnabled(): boolean {
  return import.meta.env.VITE_EXPENSES_ENABLED === "true";
}
