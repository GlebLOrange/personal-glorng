import { afterEach, describe, expect, it, vi } from "vitest";

import { DEFAULT_DESCRIPTION, DEFAULT_DOCUMENT_TITLE, formatDocumentTitle } from "@/constants/seo";
import { absoluteUrl, applyPageSeo, publicOrigin } from "@/utils/pageSeo";

afterEach(() => {
  document.title = "";
  document.head.querySelectorAll("meta[name], meta[property]").forEach((el) => el.remove());
  document.head
    .querySelectorAll('link[rel="amphtml"], link[rel="canonical"]')
    .forEach((el) => el.remove());
  document.getElementById("glorng-json-ld")?.remove();
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
    expect(absoluteUrl("/apple-touch-icon.png")).toBe("https://example.test/apple-touch-icon.png");
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

  it("removes leftover amphtml links", () => {
    const leftover = document.createElement("link");
    leftover.setAttribute("rel", "amphtml");
    leftover.setAttribute("href", "/amp");
    document.head.appendChild(leftover);

    applyPageSeo({ title: "Home", path: "/" });
    expect(document.querySelector('link[rel="amphtml"]')).toBeNull();
  });

  it("sets a canonical link matching og:url", () => {
    applyPageSeo({ title: "Tools", path: "/tools" });
    const canonical = document.querySelector('link[rel="canonical"]');
    const ogUrl = document.querySelector('meta[property="og:url"]')?.getAttribute("content");
    expect(canonical?.getAttribute("href")).toBe(ogUrl);
    expect(canonical?.getAttribute("href")).toContain("/tools");
  });

  it("injects and clears JSON-LD when requested", () => {
    applyPageSeo({
      title: "Home",
      path: "/",
      jsonLd: { "@context": "https://schema.org", "@type": "Person", name: "Gleb.Y" },
    });
    const script = document.getElementById("glorng-json-ld");
    expect(script?.getAttribute("type")).toBe("application/ld+json");
    expect(script?.textContent).toContain('"name":"Gleb.Y"');

    applyPageSeo({ title: "News", path: "/news", jsonLd: null });
    expect(document.getElementById("glorng-json-ld")).toBeNull();
  });
});
