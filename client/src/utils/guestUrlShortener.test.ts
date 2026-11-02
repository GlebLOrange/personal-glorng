import { describe, expect, it } from "vitest";

import {
  createGuestShortUrl,
  deleteGuestShortUrl,
  MAX_GUEST_SHORT_URLS,
  sanitizeGuestShortUrls,
  updateGuestShortUrlTitle,
} from "@/utils/guestUrlShortener";
import type { UrlItem } from "@/types";

function sample(overrides: Partial<UrlItem> = {}): UrlItem {
  return {
    id: -1,
    code: "Ab12Cd34",
    original_url: "https://example.com/",
    title: null,
    clicks: 0,
    created_at: "2026-01-01T00:00:00.000Z",
    ...overrides,
  };
}

describe("sanitizeGuestShortUrls", () => {
  it("drops invalid entries and caps length", () => {
    const raw = [
      sample(),
      { id: "bad" },
      sample({ id: -2, code: "short" }),
      sample({ id: -3, code: "Ef56Gh78", original_url: "javascript:alert(1)" }),
      sample({ id: -4, code: "Ij90Kl12", original_url: "https://ok.example/" }),
    ];
    const cleaned = sanitizeGuestShortUrls(raw);
    expect(cleaned).toHaveLength(2);
    expect(cleaned.map((item) => item.code)).toEqual(["Ab12Cd34", "Ij90Kl12"]);
    expect(cleaned.every((item) => item.clicks === 0)).toBe(true);
  });

  it("enforces the guest cap", () => {
    const raw = Array.from({ length: MAX_GUEST_SHORT_URLS + 5 }, (_, index) =>
      sample({
        id: -(index + 1),
        code: `Code${String(index).padStart(4, "0")}`.slice(0, 8),
        original_url: `https://example.com/${index}`,
      }),
    );
    expect(sanitizeGuestShortUrls(raw)).toHaveLength(MAX_GUEST_SHORT_URLS);
  });
});

describe("createGuestShortUrl", () => {
  it("prepends https and rejects at cap", () => {
    const created = createGuestShortUrl([], "example.com/path", "Demo");
    expect(created.ok).toBe(true);
    if (!created.ok) return;
    expect(created.item.original_url).toBe("https://example.com/path");
    expect(created.item.code).toHaveLength(8);
    expect(created.item.id).toBeLessThan(0);

    const full = Array.from({ length: MAX_GUEST_SHORT_URLS }, (_, index) =>
      sample({
        id: -(index + 1),
        code: `Code${String(index).padStart(4, "0")}`.slice(0, 8),
      }),
    );
    const blocked = createGuestShortUrl(full, "https://example.com", null);
    expect(blocked.ok).toBe(false);
  });
});

describe("update and delete guest short urls", () => {
  it("updates title and deletes by id", () => {
    const items = [sample({ id: -1, title: "Before" }), sample({ id: -2, code: "ZzYyXxWw" })];
    const updated = updateGuestShortUrlTitle(items, -1, "After");
    expect(updated.find((item) => item.id === -1)?.title).toBe("After");
    expect(deleteGuestShortUrl(updated, -1)).toHaveLength(1);
  });
});
