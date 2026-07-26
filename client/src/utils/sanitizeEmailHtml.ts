import DOMPurify from "dompurify";

function ensureLinkRel(node: Element): void {
  if (node.tagName !== "A") return;
  const rel = node.getAttribute("rel") ?? "";
  const parts = new Set(rel.split(/\s+/).filter(Boolean));
  parts.add("noopener");
  parts.add("noreferrer");
  node.setAttribute("rel", [...parts].join(" "));
}

// Register once — add/remove per call races under concurrent sanitize.
DOMPurify.addHook("afterSanitizeAttributes", ensureLinkRel);

/** Sanitize server-rendered email HTML before binding with v-html. */
export function sanitizeEmailHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    USE_PROFILES: { html: true },
    FORBID_TAGS: ["script", "iframe", "object", "embed", "form"],
  });
}
