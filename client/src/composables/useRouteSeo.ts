import { applyPageSeo } from "@/utils/pageSeo";

/**
 * Apply SEO from the active route's `meta.title` / `meta.description`.
 * Pages that need a dynamic title (e.g. news articles) call `applyPageSeo` themselves.
 */
export function applyRouteSeo(to: {
  fullPath: string;
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
  applyPageSeo({
    title,
    description,
    path: to.fullPath,
    noindex,
  });
}
