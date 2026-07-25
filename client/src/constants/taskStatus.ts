import { familyBadgeClass } from "@/constants/httpStatusColors";

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

const MUTED_BADGE = "text-surface-mid bg-surface-mid/10 border-surface-border";

const STATUS_BADGE_CLASS: Record<string, string> = {
  pending: familyBadgeClass("3xx"),
  completed: familyBadgeClass("2xx"),
  not_completed: familyBadgeClass("4xx"),
  postponed: familyBadgeClass("1xx"),
  cancelled: MUTED_BADGE,
  failed: familyBadgeClass("4xx"),
  parsing: familyBadgeClass("1xx"),
  clarifying: familyBadgeClass("1xx"),
  ready: familyBadgeClass("2xx"),
  confirmed: familyBadgeClass("2xx"),
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
  pending: "text-status-cyan hover:bg-status-cyan/15",
  completed: "text-status-success hover:bg-status-success/15",
  not_completed: "text-status-error hover:bg-status-error/15",
  postponed: "text-accent-blue hover:bg-accent-blue/15",
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
  return STATUS_BADGE_CLASS[status] ?? MUTED_BADGE;
}

/** Tailwind classes for a status action in a dropdown menu. */
export function statusMenuItemClass(status: TaskStatus): string {
  return STATUS_MENU_ITEM_CLASS[status];
}
