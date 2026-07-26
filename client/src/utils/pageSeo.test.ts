import { afterEach, describe, expect, it, vi } from "vitest";

import { DEFAULT_DESCRIPTION, DEFAULT_DOCUMENT_TITLE, formatDocumentTitle } from "@/constants/seo";
import { absoluteUrl, applyPageSeo, publicOrigin } from "@/utils/pageSeo";

afterEach(() => {
  document.title = "";
  document.head.querySelectorAll("meta[name], meta[property]").forEach((el) => el.remove());
  document.head.querySelectorAll('link[rel="amphtml"]').forEach((el) => el.remove());
  vi.unstubAllEnvs();
});

describe("formatDocumentTitle", () => {
  it("returns the default shell title when empty", () => {
    expect(formatDocumentTitle()).toBe(DEFAULT_DOCUMENT_TITLE);
    expect(formatDocumentTitle("  ")).toBe(DEFAULT_DOCUMENT_TITLE);
  });

  it("suffixes page titles with the site name", () => {
    expect(formatDocumentTitle("Tools")).toBe("Tools — Gleb.Y");
  });
});

describe("absoluteUrl / publicOrigin", () => {
  it("prefers VITE_PUBLIC_ORIGIN when set", () => {
    vi.stubEnv("VITE_PUBLIC_ORIGIN", "https://example.test/");
    expect(publicOrigin()).toBe("https://example.test");
    expect(absoluteUrl("/apple-touch-icon.png")).toBe(
      "https://example.test/apple-touch-icon.png",
    );
  });

  it("falls back to window.location.origin", () => {
    vi.stubEnv("VITE_PUBLIC_ORIGIN", "");
    expect(absoluteUrl("/tools")).toBe(`${window.location.origin}/tools`);
  });
});

describe("applyPageSeo", () => {
  it("sets document title and core meta tags", () => {
    applyPageSeo({
      title: "Tools",
      description: "Public utilities",
      path: "/tools",
    });

    expect(document.title).toBe("Tools — Gleb.Y");
    expect(document.querySelector('meta[name="description"]')?.getAttribute("content")).toBe(
      "Public utilities",
    );
    expect(document.querySelector('meta[property="og:title"]')?.getAttribute("content")).toBe(
      "Tools — Gleb.Y",
    );
    expect(document.querySelector('meta[property="og:url"]')?.getAttribute("content")).toContain(
      "/tools",
    );
    expect(document.querySelector('meta[name="robots"]')?.getAttribute("content")).toBe(
      "index, follow",
    );
  });

  it("marks private pages noindex", () => {
    applyPageSeo({ title: "Login", noindex: true, path: "/login" });
    expect(document.querySelector('meta[name="robots"]')?.getAttribute("content")).toBe(
      "noindex, nofollow",
    );
  });

  it("falls back to the default description", () => {
    applyPageSeo({ title: "Privacy policy", path: "/privacy" });
    expect(document.querySelector('meta[name="description"]')?.getAttribute("content")).toBe(
      DEFAULT_DESCRIPTION,
    );
  });

  it("sets amphtml only when requested", () => {
    applyPageSeo({ title: "Home", path: "/", amphtml: true });
    const link = document.querySelector('link[rel="amphtml"]');
    expect(link).toBeTruthy();
    expect(link?.getAttribute("href")).toContain("/amp");

    applyPageSeo({ title: "News", path: "/news", amphtml: false });
    expect(document.querySelector('link[rel="amphtml"]')).toBeNull();
  });
});
