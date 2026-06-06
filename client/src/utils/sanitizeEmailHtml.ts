import DOMPurify from "dompurify";

/** Add rel=noopener on links that survived sanitization. */
export function addLinkRelAttributes(html: string): string {
  return html.replace(
    /<a\s+((?![^>]*\brel=)[^>]*href="[^"]*"[^>]*)>/gi,
    '<a $1 rel="noopener noreferrer">',
  );
}

/** Sanitize server-rendered email HTML before binding with v-html. */
export function sanitizeEmailHtml(html: string): string {
  const clean = DOMPurify.sanitize(html, {
    USE_PROFILES: { html: true },
    FORBID_TAGS: ["script", "iframe", "object", "embed", "form"],
    FORBID_ATTR: ["onerror", "onload", "onclick", "onmouseover"],
  });
  return addLinkRelAttributes(clean);
}
