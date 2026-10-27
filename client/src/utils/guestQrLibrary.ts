import type { QrErrorLevel, QrListItem, QrStoredItem } from "@/types";

/** localStorage key for guest (no qr-generator read) saved QR codes. */
export const GUEST_QR_LIBRARY_KEY = "guest-qr-library";

/** ponytail: localStorage demo cap — raise or move to IndexedDB if guests need more. */
export const MAX_GUEST_QR_CODES = 20;

const MAX_CONTENT_LENGTH = 2000;
const MAX_LABEL_LENGTH = 120;
const ERROR_LEVELS = new Set<QrErrorLevel>(["L", "M", "Q", "H"]);

export function guestQrLimitMessage(currentCount: number): string {
  return `${currentCount}/${MAX_GUEST_QR_CODES} QR codes saved in your browser`;
}

function trimField(value: unknown, maxLength: number): string {
  if (typeof value !== "string") {
    return "";
  }
  return value.trim().slice(0, maxLength);
}

function isErrorLevel(value: unknown): value is QrErrorLevel {
  return typeof value === "string" && ERROR_LEVELS.has(value as QrErrorLevel);
}

function isGuestQrStored(value: unknown): value is QrStoredItem {
  if (!value || typeof value !== "object") {
    return false;
  }
  const record = value as Record<string, unknown>;
  return (
    typeof record.id === "number" &&
    Number.isFinite(record.id) &&
    typeof record.content === "string" &&
    typeof record.svg === "string" &&
    typeof record.created_at === "string" &&
    typeof record.updated_at === "string" &&
    isErrorLevel(record.error_level)
  );
}

export function svgToDataUrl(svg: string): string {
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

export function contentPreview(content: string, maxLength = 80): string {
  const trimmed = content.trim();
  if (trimmed.length <= maxLength) {
    return trimmed;
  }
  return `${trimmed.slice(0, maxLength - 1)}…`;
}

/** Validate and cap guest QR library loaded from localStorage. */
export function sanitizeGuestQrLibrary(raw: unknown): QrStoredItem[] {
  if (!Array.isArray(raw)) {
    return [];
  }

  const seenIds = new Set<number>();
  const sanitized: QrStoredItem[] = [];

  for (const item of raw) {
    if (sanitized.length >= MAX_GUEST_QR_CODES) {
      break;
    }
    if (!isGuestQrStored(item) || seenIds.has(item.id)) {
      continue;
    }

    const content = trimField(item.content, MAX_CONTENT_LENGTH);
    const svg = typeof item.svg === "string" ? item.svg.trim() : "";
    if (!content || !svg) {
      continue;
    }

    const labelRaw = item.label;
    const label = labelRaw == null ? null : trimField(labelRaw, MAX_LABEL_LENGTH) || null;

    seenIds.add(item.id);
    sanitized.push({
      id: item.id,
      content,
      content_preview: contentPreview(content),
      label,
      error_level: item.error_level,
      svg,
      svg_url: svgToDataUrl(svg),
      created_at: item.created_at,
      updated_at: item.updated_at,
    });
  }

  return sanitized;
}

export function nextGuestQrId(items: Array<{ id: number }>): number {
  let min = 0;
  for (const item of items) {
    if (item.id < min) {
      min = item.id;
    }
  }
  return min - 1;
}

export function toGuestQrListItem(item: QrStoredItem): QrListItem {
  return {
    id: item.id,
    content_preview: item.content_preview,
    label: item.label,
    error_level: item.error_level,
    svg_url: item.svg_url || svgToDataUrl(item.svg ?? ""),
    created_at: item.created_at,
    updated_at: item.updated_at,
  };
}

export function createGuestQr(
  items: QrStoredItem[],
  input: {
    content: string;
    label: string | null;
    error_level: QrErrorLevel;
    svg: string;
  },
): { ok: true; item: QrStoredItem; next: QrStoredItem[] } | { ok: false; error: string } {
  if (items.length >= MAX_GUEST_QR_CODES) {
    return { ok: false, error: guestQrLimitMessage(items.length) };
  }
  const content = trimField(input.content, MAX_CONTENT_LENGTH);
  const svg = input.svg.trim();
  if (!content || !svg) {
    return { ok: false, error: "Generate a QR code before saving" };
  }
  if (!isErrorLevel(input.error_level)) {
    return { ok: false, error: "Invalid error correction level" };
  }

  const now = new Date().toISOString();
  const item: QrStoredItem = {
    id: nextGuestQrId(items),
    content,
    content_preview: contentPreview(content),
    label: input.label?.trim() ? input.label.trim().slice(0, MAX_LABEL_LENGTH) : null,
    error_level: input.error_level,
    svg,
    svg_url: svgToDataUrl(svg),
    created_at: now,
    updated_at: now,
  };

  return { ok: true, item, next: [item, ...items] };
}

export function updateGuestQr(
  items: QrStoredItem[],
  id: number,
  input: {
    content: string;
    label: string | null;
    error_level: QrErrorLevel;
    svg: string;
  },
): { ok: true; item: QrStoredItem; next: QrStoredItem[] } | { ok: false; error: string } {
  const index = items.findIndex((item) => item.id === id);
  if (index === -1) {
    return { ok: false, error: "Saved QR code not found" };
  }
  const content = trimField(input.content, MAX_CONTENT_LENGTH);
  const svg = input.svg.trim();
  if (!content || !svg) {
    return { ok: false, error: "Generate a QR code before saving" };
  }
  if (!isErrorLevel(input.error_level)) {
    return { ok: false, error: "Invalid error correction level" };
  }

  const prev = items[index]!;
  const item: QrStoredItem = {
    ...prev,
    content,
    content_preview: contentPreview(content),
    label: input.label?.trim() ? input.label.trim().slice(0, MAX_LABEL_LENGTH) : null,
    error_level: input.error_level,
    svg,
    svg_url: svgToDataUrl(svg),
    updated_at: new Date().toISOString(),
  };
  const next = [...items];
  next[index] = item;
  return { ok: true, item, next };
}

export function deleteGuestQr(items: QrStoredItem[], id: number): QrStoredItem[] {
  return items.filter((item) => item.id !== id);
}
