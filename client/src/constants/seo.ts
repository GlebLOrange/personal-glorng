/** Site-wide SEO defaults for the CSR SPA shell. */
export const SITE_NAME = "Gleb.Y";
export const DEFAULT_DOCUMENT_TITLE = `${SITE_NAME} — Python Backend / FastAPI Engineer`;
export const DEFAULT_DESCRIPTION =
  "Gleb.Y — Python Backend / FastAPI Engineer. Production APIs, auth, workers, data stores, and CI/CD. Full-stack capable.";

export function formatDocumentTitle(pageTitle?: string | null): string {
  const trimmed = pageTitle?.trim();
  if (!trimmed) return DEFAULT_DOCUMENT_TITLE;
  if (trimmed === DEFAULT_DOCUMENT_TITLE || trimmed === SITE_NAME) return trimmed;
  return `${trimmed} — ${SITE_NAME}`;
}
