import { formatDate } from "@/utils/format";

/** Shared copy for expense calculator persistence status. */
export function buildPersistenceHint(input: {
  isSuperuser: boolean;
  stateDirty: boolean;
  lastSavedAt: string | null;
}): string {
  if (input.isSuperuser) {
    if (input.lastSavedAt && !input.stateDirty) {
      return `saved ${formatDate(input.lastSavedAt)}`;
    }
    if (input.stateDirty) return "unsaved changes";
    return "superuser: save to keep data across sessions";
  }
  return "calculations reset when you leave this page.";
}
