import {
  DEFAULT_DESCRIPTION,
  DEFAULT_DOCUMENT_TITLE,
  formatDocumentTitle,
  SITE_NAME,
} from "@/constants/seo";

export type PageSeoInput = {
  title?: string | null;
  description?: string | null;
  image?: string | null;
  /** Absolute or root-relative path; defaults to current location. */
  path?: string | null;
  noindex?: boolean;
};

function upsertMeta(attr: "name" | "property", key: string, content: string): void {
  const selector = `meta[${attr}="${key}"]`;
  let el = document.head.querySelector(selector);
  if (!(el instanceof HTMLMetaElement)) {
    el = document.createElement("meta");
    el.setAttribute(attr, key);
    document.head.appendChild(el);
  }
  el.setAttribute("content", content);
}

function absoluteUrl(pathOrUrl: string): string {
  if (/^https?:\/\//i.test(pathOrUrl)) return pathOrUrl;
  const path = pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`;
  return new URL(path, window.location.origin).href;
}

/**
 * Apply document title + description / Open Graph / Twitter tags for the current view.
 * Safe for CSR only (touches `document`).
 */
export function applyPageSeo(input: PageSeoInput = {}): void {
  const title = formatDocumentTitle(input.title);
  const description = (input.description?.trim() || DEFAULT_DESCRIPTION).slice(0, 300);
  const path = input.path ?? `${window.location.pathname}${window.location.search}`;
  const url = absoluteUrl(path);
  const image = absoluteUrl(input.image?.trim() || "/apple-touch-icon.png");

  document.title = title;

  upsertMeta("name", "description", description);
  upsertMeta("name", "robots", input.noindex ? "noindex, nofollow" : "index, follow");

  upsertMeta("property", "og:site_name", SITE_NAME);
  upsertMeta("property", "og:type", "website");
  upsertMeta("property", "og:title", title);
  upsertMeta("property", "og:description", description);
  upsertMeta("property", "og:url", url);
  upsertMeta("property", "og:image", image);

  upsertMeta("name", "twitter:card", "summary");
  upsertMeta("name", "twitter:title", title);
  upsertMeta("name", "twitter:description", description);
  upsertMeta("name", "twitter:image", image);
}

/** Reset to the default portfolio SEO shell (used by catch-all / errors). */
export function applyDefaultPageSeo(): void {
  applyPageSeo({
    title: DEFAULT_DOCUMENT_TITLE,
    description: DEFAULT_DESCRIPTION,
    path: "/",
  });
}
