import { describe, expect, it } from "vitest";

import { RESUME_FALLBACK } from "@/constants/resumeFallback";
import {
  buildGlanceStats,
  computeYearsExperience,
  countSkills,
  primaryStack,
} from "@/utils/resumeGlance";

describe("resumeGlance", () => {
  it("computes years of experience from period strings", () => {
    expect(computeYearsExperience(RESUME_FALLBACK.experience)).toBeGreaterThan(0);
  });

  it("counts skills across groups", () => {
    expect(countSkills(RESUME_FALLBACK.skills)).toBeGreaterThan(10);
  });

  it("builds primary stack from backend and frontend groups", () => {
    const stack = primaryStack(RESUME_FALLBACK.skills);
    expect(stack).toContain("FastAPI");
    expect(stack).toContain("Vue 3");
  });

  it("builds glance stats with availability when present", () => {
    const stats = buildGlanceStats(RESUME_FALLBACK);
    expect(stats).toHaveLength(4);
    expect(stats.find((s) => s.label === "Availability")?.value).toBe("Open");
    expect(stats.find((s) => s.label === "Core stack")?.value).toContain("FastAPI");
  });
});
