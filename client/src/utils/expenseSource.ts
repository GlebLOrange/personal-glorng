const SOURCE_LABELS: Record<string, string> = {
  web_admin: "Web",
  todobot: "Telegram",
};

/** Human-readable label for an expense source code. */
export function expenseSourceLabel(source: string): string {
  return SOURCE_LABELS[source] ?? source;
}
