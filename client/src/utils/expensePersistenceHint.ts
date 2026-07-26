/** Shared copy for expense calculator persistence status. */
export function buildPersistenceHint(input: {
  isSuperuser: boolean;
  stateDirty: boolean;
  lastSavedAt: string | null;
}): string {
  if (input.isSuperuser) {
    if (input.lastSavedAt && !input.stateDirty) {
      return `Saved ${new Date(input.lastSavedAt).toLocaleString()}`;
    }
    if (input.stateDirty) return "Unsaved changes";
    return "Superuser: save to keep data across sessions";
  }
  return "Calculations reset when you leave this page.";
}
