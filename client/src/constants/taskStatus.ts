export const TASK_STATUSES = [
  "pending",
  "completed",
  "not_completed",
  "postponed",
  "cancelled",
] as const;

export type TaskStatus = (typeof TASK_STATUSES)[number];

const STATUS_LABELS: Record<string, string> = {
  pending: "pending",
  completed: "completed",
  not_completed: "not completed",
  postponed: "postponed",
  cancelled: "cancelled",
  failed: "failed",
  parsing: "parsing",
  clarifying: "clarifying",
  ready: "ready",
  confirmed: "confirmed",
};

const STATUS_BADGE_CLASS: Record<string, string> = {
  pending: "text-status-warning bg-status-warning/10 border-status-warning/30",
  completed: "text-status-success bg-status-success/10 border-status-success/30",
  not_completed: "text-status-error bg-status-error/10 border-status-error/30",
  postponed: "text-accent-blue bg-accent-blue/10 border-accent-blue/30",
  cancelled: "text-surface-mid bg-surface-mid/10 border-surface-border",
  failed: "text-status-error bg-status-error/10 border-status-error/30",
  parsing: "text-accent-blue bg-accent-blue/10 border-accent-blue/30",
  clarifying: "text-accent-blue bg-accent-blue/10 border-accent-blue/30",
  ready: "text-status-success bg-status-success/10 border-status-success/30",
  confirmed: "text-status-success bg-status-success/10 border-status-success/30",
};

const STATUS_ACTION_LABELS: Record<TaskStatus, string> = {
  pending: "reopen",
  completed: "mark complete",
  not_completed: "didn't finish",
  postponed: "postpone",
  cancelled: "cancel task",
};

/** Text + soft hover for status change menu items. */
const STATUS_MENU_ITEM_CLASS: Record<TaskStatus, string> = {
  pending: "text-status-warning hover:bg-status-warning/10",
  completed: "text-status-success hover:bg-status-success/10",
  not_completed: "text-status-error hover:bg-status-error/10",
  postponed: "text-accent-blue hover:bg-accent-blue/10",
  cancelled: "text-surface-mid hover:bg-surface-mid/10",
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

/** Tailwind classes for a status action in a dropdown menu. */
export function statusMenuItemClass(status: TaskStatus): string {
  return STATUS_MENU_ITEM_CLASS[status];
}
