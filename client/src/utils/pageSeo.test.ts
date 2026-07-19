import { afterEach, describe, expect, it } from "vitest";

import { DEFAULT_DESCRIPTION, DEFAULT_DOCUMENT_TITLE, formatDocumentTitle } from "@/constants/seo";
import { applyPageSeo } from "@/utils/pageSeo";

afterEach(() => {
  document.title = "";
  document.head.querySelectorAll("meta[name], meta[property]").forEach((el) => el.remove());
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
});
