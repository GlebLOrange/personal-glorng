import { DEFAULT_DESCRIPTION, SITE_NAME } from "@/constants/seo";
import { RESUME_FALLBACK } from "@/constants/resumeFallback";
import { absoluteUrl, applyPageSeo } from "@/utils/pageSeo";
import { scrubSensitivePath } from "@/utils/sensitiveUrl";

function portfolioJsonLd(): Record<string, unknown> {
  const resume = RESUME_FALLBACK;
  const sameAs = [resume.links.github, resume.links.telegram, resume.links.linkedin].filter(
    (value): value is string => Boolean(value),
  );
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebSite",
        name: SITE_NAME,
        url: absoluteUrl("/"),
        description: DEFAULT_DESCRIPTION,
      },
      {
        "@type": "Person",
        name: resume.name,
        jobTitle: resume.title,
        description: resume.tagline || resume.bio,
        url: absoluteUrl("/"),
        ...(resume.location
          ? { address: { "@type": "PostalAddress", addressRegion: resume.location } }
          : {}),
        ...(sameAs.length > 0 ? { sameAs } : {}),
      },
    ],
  };
}

/**
 * Apply SEO from the active route's `meta.title` / `meta.description`.
 * Pages that need a dynamic title (e.g. news articles) call `applyPageSeo` themselves.
 */
export function applyRouteSeo(to: {
  fullPath: string;
  name?: unknown;
  meta: {
    title?: unknown;
    description?: unknown;
    noindex?: unknown;
    requiresAuth?: unknown;
  };
}): void {
  const title = typeof to.meta.title === "string" ? to.meta.title : undefined;
  const description = typeof to.meta.description === "string" ? to.meta.description : undefined;
  const noindex = to.meta.noindex === true || to.meta.requiresAuth === true;
  // Auth/noindex pages: pathname only (no secrets in og:url). Otherwise scrub sensitive query keys.
  const scrubbed = scrubSensitivePath(to.fullPath);
  const pathname = scrubbed.replace(/[?#].*$/, "");
  const isPortfolio = to.name === "portfolio" || pathname === "/";
  applyPageSeo({
    title,
    description,
    path: noindex ? pathname : scrubbed,
    noindex,
    jsonLd: isPortfolio ? portfolioJsonLd() : null,
  });
}
