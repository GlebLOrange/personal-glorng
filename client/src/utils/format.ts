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
