import { describe, expect, it } from "vitest";

import {
  createGuestQr,
  deleteGuestQr,
  MAX_GUEST_QR_CODES,
  sanitizeGuestQrLibrary,
  svgToDataUrl,
  updateGuestQr,
} from "@/utils/guestQrLibrary";
import type { QrStoredItem } from "@/types";

const SAMPLE_SVG = '<svg xmlns="http://www.w3.org/2000/svg"></svg>';

function sample(overrides: Partial<QrStoredItem> = {}): QrStoredItem {
  return {
    id: -1,
    content: "https://example.com",
    content_preview: "https://example.com",
    label: "demo",
    error_level: "M",
    svg: SAMPLE_SVG,
    svg_url: svgToDataUrl(SAMPLE_SVG),
    created_at: "2026-01-01T00:00:00.000Z",
    updated_at: "2026-01-01T00:00:00.000Z",
    ...overrides,
  };
}

describe("sanitizeGuestQrLibrary", () => {
  it("keeps valid rows and rebuilds data urls", () => {
    const cleaned = sanitizeGuestQrLibrary([
      sample(),
      { id: -2 },
      sample({ id: -3, content: "", svg: SAMPLE_SVG }),
      sample({ id: -4, content: "hello", label: null }),
    ]);
    expect(cleaned).toHaveLength(2);
    expect(cleaned[0]?.svg_url.startsWith("data:image/svg+xml")).toBe(true);
    expect(cleaned[1]?.content).toBe("hello");
  });

  it("enforces the guest cap", () => {
    const raw = Array.from({ length: MAX_GUEST_QR_CODES + 3 }, (_, index) =>
      sample({ id: -(index + 1), content: `payload-${index}` }),
    );
    expect(sanitizeGuestQrLibrary(raw)).toHaveLength(MAX_GUEST_QR_CODES);
  });
});

describe("createGuestQr and updateGuestQr", () => {
  it("creates negative ids and updates in place", () => {
    const created = createGuestQr([], {
      content: "https://glorng.dev",
      label: "site",
      error_level: "Q",
      svg: SAMPLE_SVG,
    });
    expect(created.ok).toBe(true);
    if (!created.ok) return;
    expect(created.item.id).toBeLessThan(0);
    expect(created.item.error_level).toBe("Q");

    const updated = updateGuestQr(created.next, created.item.id, {
      content: "updated",
      label: null,
      error_level: "H",
      svg: SAMPLE_SVG,
    });
    expect(updated.ok).toBe(true);
    if (!updated.ok) return;
    expect(updated.item.content).toBe("updated");
    expect(updated.item.label).toBeNull();
    expect(updated.item.error_level).toBe("H");
  });

  it("rejects create at cap", () => {
    const full = Array.from({ length: MAX_GUEST_QR_CODES }, (_, index) =>
      sample({ id: -(index + 1), content: `payload-${index}` }),
    );
    const blocked = createGuestQr(full, {
      content: "more",
      label: null,
      error_level: "M",
      svg: SAMPLE_SVG,
    });
    expect(blocked.ok).toBe(false);
  });
});

describe("deleteGuestQr", () => {
  it("removes by id", () => {
    const items = [sample({ id: -1 }), sample({ id: -2, content: "b" })];
    expect(deleteGuestQr(items, -1)).toHaveLength(1);
  });
});
