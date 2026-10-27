import type { UrlItem } from "@/types";
import { ensureHttpsUrl } from "@/utils/safeUrl";

/** localStorage key for guest (no url-shortener read) shortened URLs. */
export const GUEST_URL_SHORTENER_KEY = "guest-url-shortener";

/** ponytail: localStorage demo cap — raise or move to IndexedDB if guests need more. */
export const MAX_GUEST_SHORT_URLS = 50;

const CODE_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
const CODE_LENGTH = 8;
const MAX_ORIGINAL_URL_LENGTH = 2048;
const MAX_TITLE_LENGTH = 200;

export function guestUrlLimitMessage(currentCount: number): string {
  return `${currentCount}/${MAX_GUEST_SHORT_URLS} short links saved in your browser`;
}

function trimField(value: unknown, maxLength: number): string {
  if (typeof value !== "string") {
    return "";
  }
  return value.trim().slice(0, maxLength);
}

function isGuestUrlItem(value: unknown): value is UrlItem {
  if (!value || typeof value !== "object") {
    return false;
  }
  const record = value as Record<string, unknown>;
  return (
    typeof record.id === "number" &&
    Number.isFinite(record.id) &&
    typeof record.code === "string" &&
    typeof record.original_url === "string" &&
    typeof record.created_at === "string"
  );
}

function isHttpUrl(raw: string): boolean {
  try {
    const parsed = new URL(ensureHttpsUrl(raw));
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

/** Validate and cap guest short URLs loaded from localStorage. */
export function sanitizeGuestShortUrls(raw: unknown): UrlItem[] {
  if (!Array.isArray(raw)) {
    return [];
  }

  const seenCodes = new Set<string>();
  const sanitized: UrlItem[] = [];

  for (const item of raw) {
    if (sanitized.length >= MAX_GUEST_SHORT_URLS) {
      break;
    }
    if (!isGuestUrlItem(item)) {
      continue;
    }

    const code = trimField(item.code, CODE_LENGTH);
    if (!/^[a-zA-Z0-9]{8}$/.test(code) || seenCodes.has(code)) {
      continue;
    }

    const original = trimField(item.original_url, MAX_ORIGINAL_URL_LENGTH);
    if (!isHttpUrl(original)) {
      continue;
    }

    const titleRaw = item.title;
    const title = titleRaw == null ? null : trimField(titleRaw, MAX_TITLE_LENGTH) || null;

    seenCodes.add(code);
    sanitized.push({
      id: item.id,
      code,
      original_url: ensureHttpsUrl(original),
      title,
      clicks: 0,
      created_at: item.created_at,
    });
  }

  return sanitized;
}

/** 8-character alphanumeric code (crypto when available). */
export function generateGuestShortCode(): string {
  const bytes = new Uint8Array(CODE_LENGTH);
  crypto.getRandomValues(bytes);
  let out = "";
  for (let i = 0; i < CODE_LENGTH; i += 1) {
    out += CODE_ALPHABET[bytes[i]! % CODE_ALPHABET.length]!;
  }
  return out;
}

/** Next negative id so guest rows never collide with server ids. */
export function nextGuestUrlId(items: UrlItem[]): number {
  let min = 0;
  for (const item of items) {
    if (item.id < min) {
      min = item.id;
    }
  }
  return min - 1;
}

export function createGuestShortUrl(
  items: UrlItem[],
  originalUrl: string,
  title: string | null,
): { ok: true; item: UrlItem; next: UrlItem[] } | { ok: false; error: string } {
  if (items.length >= MAX_GUEST_SHORT_URLS) {
    return { ok: false, error: guestUrlLimitMessage(items.length) };
  }
  const normalized = ensureHttpsUrl(originalUrl.trim());
  if (!isHttpUrl(normalized)) {
    return { ok: false, error: "enter a full URL like https://example.com" };
  }

  const used = new Set(items.map((item) => item.code));
  let code = generateGuestShortCode();
  let attempts = 0;
  while (used.has(code) && attempts < 16) {
    code = generateGuestShortCode();
    attempts += 1;
  }
  if (used.has(code)) {
    return { ok: false, error: "Could not allocate a unique short code" };
  }

  let original_url = normalized;
  try {
    const parsed = new URL(normalized);
    if (parsed.pathname === "" || parsed.pathname === "/") {
      original_url = `${parsed.origin}/`;
    }
  } catch {
    // keep normalized
  }

  const item: UrlItem = {
    id: nextGuestUrlId(items),
    code,
    original_url,
    title: title?.trim() ? title.trim().slice(0, MAX_TITLE_LENGTH) : null,
    clicks: 0,
    created_at: new Date().toISOString(),
  };

  return { ok: true, item, next: [item, ...items] };
}

export function updateGuestShortUrlTitle(
  items: UrlItem[],
  id: number,
  title: string | null,
): UrlItem[] {
  const trimmed = title?.trim() ? title.trim().slice(0, MAX_TITLE_LENGTH) : null;
  return items.map((item) => (item.id === id ? { ...item, title: trimmed } : item));
}

export function deleteGuestShortUrl(items: UrlItem[], id: number): UrlItem[] {
  return items.filter((item) => item.id !== id);
}
