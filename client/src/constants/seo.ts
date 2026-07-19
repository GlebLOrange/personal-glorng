/** Site-wide SEO defaults for the CSR SPA shell. */
export const SITE_NAME = "Gleb.Y";
export const DEFAULT_DOCUMENT_TITLE = `${SITE_NAME} — Developer Portfolio`;
export const DEFAULT_DESCRIPTION =
  "Gleb.Y — developer portfolio, tools, and curated news. Full-stack delivery of web apps, APIs, and product platforms.";

export function formatDocumentTitle(pageTitle?: string | null): string {
  const trimmed = pageTitle?.trim();
  if (!trimmed) return DEFAULT_DOCUMENT_TITLE;
  if (trimmed === DEFAULT_DOCUMENT_TITLE || trimmed === SITE_NAME) return trimmed;
  return `${trimmed} — ${SITE_NAME}`;
}
