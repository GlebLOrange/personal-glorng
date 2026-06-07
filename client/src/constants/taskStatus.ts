export const TASK_STATUSES = [
  "pending",
  "completed",
  "not_completed",
  "postponed",
  "cancelled",
] as const;

export type TaskStatus = (typeof TASK_STATUSES)[number];

const STATUS_LABELS: Record<string, string> = {
  pending: "Pending",
  completed: "Completed",
  not_completed: "Not completed",
  postponed: "Postponed",
  cancelled: "Cancelled",
  failed: "Failed",
  parsing: "Parsing",
  clarifying: "Clarifying",
  ready: "Ready",
  confirmed: "Confirmed",
};

const STATUS_BADGE_CLASS: Record<string, string> = {
  pending: "text-yellow-400 bg-yellow-400/10 border-yellow-400/30",
  completed: "text-green-400 bg-green-400/10 border-green-400/30",
  not_completed: "text-red-400 bg-red-400/10 border-red-400/30",
  postponed: "text-blue-400 bg-blue-400/10 border-blue-400/30",
  cancelled: "text-surface-mid bg-surface-mid/10 border-surface-border",
  failed: "text-red-400 bg-red-400/10 border-red-400/30",
  parsing: "text-accent-blue bg-accent-blue/10 border-accent-blue/30",
  clarifying: "text-accent-blue bg-accent-blue/10 border-accent-blue/30",
  ready: "text-green-400 bg-green-400/10 border-green-400/30",
  confirmed: "text-green-400 bg-green-400/10 border-green-400/30",
};

const STATUS_ACTION_LABELS: Record<TaskStatus, string> = {
  pending: "Reopen",
  completed: "Mark complete",
  not_completed: "Didn't finish",
  postponed: "Postpone",
  cancelled: "Cancel task",
};

/** Human-readable label for a task or intake status. */
export function statusLabel(status: string): string {
  return STATUS_LABELS[status] ?? status.replaceAll("_", " ");
}

/** Verb-based label for status change actions. */
export function statusActionLabel(status: TaskStatus): string {
  return STATUS_ACTION_LABELS[status];
}

/** Tailwind classes for a status badge. */
export function statusBadgeClass(status: string): string {
  return STATUS_BADGE_CLASS[status] ?? "text-surface-mid bg-surface-mid/10 border-surface-border";
}
