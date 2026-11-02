/** Human title from a URL's slug: last path segment, else hostname. */
export function urlSlugTitle(rawUrl: string): string {
  let url: URL;
  try {
    url = new URL(/^https?:\/\//i.test(rawUrl) ? rawUrl : `https://${rawUrl}`);
  } catch {
    return rawUrl;
  }
  const segment = url.pathname.split("/").filter(Boolean).pop() ?? "";
  const base = decodeURIComponent(segment).replace(/\.[a-z0-9]{1,5}$/i, "");
  const words = base.replace(/[-_+.]+/g, " ").trim();
  return words || url.hostname.replace(/^www\./, "");
}
