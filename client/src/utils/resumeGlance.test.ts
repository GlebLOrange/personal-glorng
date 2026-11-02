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

  it("builds hiring glance stats from years, shipped systems, and availability", () => {
    const stats = buildGlanceStats(RESUME_FALLBACK);
    expect(stats.find((s) => s.label === "Experience")?.value).toMatch(/^\d+\+$/);
    expect(stats.find((s) => s.label === "Experience")?.href).toBe("#experience");
    expect(Number(stats.find((s) => s.label === "Case studies")?.value)).toBeGreaterThan(0);
    expect(stats.find((s) => s.label === "Case studies")?.href).toBe("#case-studies");
    expect(stats.find((s) => s.label === "Availability")?.value).toBe("open");
    expect(stats.find((s) => s.label === "Availability")?.href).toBe("#contacts");
  });
});
