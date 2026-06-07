export function formatBreadcrumbLabel(title: string): string {
  return title
    .split(/[\s-]+/)
    .filter(Boolean)
    .join(" ");
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function startOfLocalDay(d: Date): number {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
}

function localDayDiff(from: Date, to: Date): number {
  return Math.round((startOfLocalDay(to) - startOfLocalDay(from)) / 86_400_000);
}

function formatTimeShort(d: Date): string {
  return d
    .toLocaleString("en-GB", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    })
    .toLowerCase();
}

/** Relative headline plus absolute detail for scheduled datetimes. */
export function formatScheduleDate(iso: string): { headline: string; detail: string } {
  const date = new Date(iso);
  const now = new Date();
  const detail = formatDate(iso);
  const dayDiff = localDayDiff(now, date);
  const msDiff = date.getTime() - now.getTime();

  if (dayDiff === 0) {
    return { headline: `Today at ${formatTimeShort(date)}`, detail };
  }
  if (dayDiff === 1) {
    return { headline: `Tomorrow at ${formatTimeShort(date)}`, detail };
  }
  if (dayDiff === -1) {
    return { headline: `Yesterday at ${formatTimeShort(date)}`, detail };
  }
  if (msDiff > 0 && msDiff < 86_400_000) {
    const hours = Math.max(1, Math.round(msDiff / 3_600_000));
    return {
      headline: `In ${hours} hour${hours === 1 ? "" : "s"}`,
      detail,
    };
  }
  if (msDiff < 0) {
    const days = Math.abs(dayDiff);
    if (days <= 7) {
      return {
        headline: `${days} day${days === 1 ? "" : "s"} ago`,
        detail,
      };
    }
  }
  if (dayDiff > 0 && dayDiff <= 7) {
    return { headline: `In ${dayDiff} days`, detail };
  }

  return { headline: detail, detail: "" };
}

/** Short past-relative label for history timestamps. */
export function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) {
    return "just now";
  }
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 60) {
    return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  }
  const hours = Math.floor(minutes / 60);
  if (hours < 24) {
    return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  }
  const days = Math.floor(hours / 24);
  if (days < 7) {
    return `${days} day${days === 1 ? "" : "s"} ago`;
  }
  const weeks = Math.floor(days / 7);
  if (weeks < 5) {
    return `${weeks} week${weeks === 1 ? "" : "s"} ago`;
  }
  return formatDate(iso);
}

/** Human-readable byte size. */
export function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** Remaining time until expiry ISO timestamp. */
export function formatTimeRemaining(expiresAt: string): string {
  const diff = new Date(expiresAt).getTime() - Date.now();
  if (diff <= 0) {
    return "expired";
  }
  const hours = Math.floor(diff / 3_600_000);
  const minutes = Math.floor((diff % 3_600_000) / 60_000);
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}
