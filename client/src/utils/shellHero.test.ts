import { describe, expect, it } from "vitest";

import { RESUME_FALLBACK } from "@/constants/resumeFallback";
import { buildShellHeroHtml, escapeHtml } from "@/utils/shellHero";

describe("shellHero", () => {
  it("escapes HTML special characters", () => {
    expect(escapeHtml(`<a href="x">&'`)).toBe("&lt;a href=&quot;x&quot;&gt;&amp;&#39;");
  });

  it("builds a short hero from resume fallback", () => {
    const html = buildShellHeroHtml();
    expect(html).toContain(`>${RESUME_FALLBACK.name}<`);
    expect(html).toContain(RESUME_FALLBACK.title);
    expect(html).toContain(RESUME_FALLBACK.tagline!);
    expect(html).toContain(RESUME_FALLBACK.availability!);
    expect(html).not.toContain("<script");
  });
});
