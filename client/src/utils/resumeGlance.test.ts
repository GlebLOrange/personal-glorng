import { describe, expect, it } from "vitest";

import { RESUME_FALLBACK } from "@/constants/resumeFallback";
import {
  buildGlanceStats,
  computeYearsExperience,
  countSkills,
  primaryStack,
} from "@/utils/resumeGlance";

describe("resumeGlance", () => {
  it("keeps offline case-study urls aligned with resume_data", () => {
    const auth = RESUME_FALLBACK.projects.find((project) => project.name === "cookie auth & CSRF");
    const ssrf = RESUME_FALLBACK.projects.find(
      (project) => project.name === "SSRF-safe outbound fetch",
    );
    expect(auth?.url).toContain("csrf-and-cors");
    expect(ssrf?.url).toContain("url_safety.py");
    expect(auth?.result).toBeTruthy();
    expect(ssrf?.result).toBeTruthy();
  });

  it("computes years of experience from period strings", () => {
    expect(computeYearsExperience(RESUME_FALLBACK.experience)).toBeGreaterThan(0);
  });

  it("counts skills across groups", () => {
    expect(countSkills(RESUME_FALLBACK.skills)).toBeGreaterThan(10);
  });

  it("builds primary stack from backend and frontend groups", () => {
    // backend[0] · frontend[0] · backend[1] from RESUME_FALLBACK.skills
    const stack = primaryStack(RESUME_FALLBACK.skills);
    expect(stack).toBe("Python · Vue 3 · FastAPI");
  });

  it("builds glance stats from case-study outcomes plus availability", () => {
    const stats = buildGlanceStats(RESUME_FALLBACK);
    expect(stats).toHaveLength(4);
    expect(stats.find((s) => s.label === "Availability")?.value).toBe("open");
    expect(stats.find((s) => s.label === "cookie auth & CSRF")?.value).toBe("CSRF");
    expect(stats.find((s) => s.label === "SSRF-safe outbound fetch")?.value).toBe("SSRF-safe");
    expect(stats.find((s) => s.label === "Platform sample")?.value).toBe("since 2022");
    expect(stats.find((s) => s.label === "cookie auth & CSRF")?.href).toBe("#case-studies");
    expect(stats.find((s) => s.label === "SSRF-safe outbound fetch")?.href).toBe("#case-studies");
    expect(stats.find((s) => s.label === "Platform sample")?.href).toBe("#experience");
    expect(stats.find((s) => s.label === "Availability")?.href).toBe("#contacts");
  });
});
