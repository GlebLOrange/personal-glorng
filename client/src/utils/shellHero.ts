import { RESUME_FALLBACK } from "../constants/resumeFallback";
import type { ResumeData } from "../types";

/** Escape text for injection into the static HTML shell. */
export function escapeHtml(text: string): string {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

/**
 * Short no-JS / crawler hero from resume data.
 * Vue replaces `#app` on mount; this only matters before the SPA boots.
 */
export function buildShellHeroHtml(resume: ResumeData = RESUME_FALLBACK): string {
  const tagline = resume.tagline?.trim() || resume.title;
  const parts = [
    `<main class="shell-hero" style="font-family:'IBM Plex Sans',Segoe UI,system-ui,sans-serif;max-width:40rem;margin:2.5rem auto;padding:0 1.5rem;color:#e6edf3" aria-label="Portfolio summary">`,
    `<h1 style="font-size:2rem;font-weight:700;margin:0 0 0.5rem">${escapeHtml(resume.name)}</h1>`,
    `<p style="margin:0 0 0.75rem;font-size:1.125rem;color:#c9d1d9">${escapeHtml(resume.title)}</p>`,
    `<p style="margin:0 0 0.75rem;line-height:1.5;color:#8b949e">${escapeHtml(tagline)}</p>`,
  ];
  if (resume.availability) {
    parts.push(
      `<p style="margin:0;font-size:0.875rem;color:#8b949e">${escapeHtml(resume.availability)}</p>`,
    );
  }
  parts.push("</main>");
  return parts.join("");
}
