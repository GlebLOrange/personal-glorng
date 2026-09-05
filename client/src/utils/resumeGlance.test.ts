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
    // backend[0] · frontend[0] · backend[2] from RESUME_FALLBACK.skills
    const stack = primaryStack(RESUME_FALLBACK.skills);
    expect(stack).toBe("Python · Vue 3 · Django");
  });

  it("builds glance stats with availability when present", () => {
    const stats = buildGlanceStats(RESUME_FALLBACK);
    expect(stats).toHaveLength(4);
    expect(stats.find((s) => s.label === "Availability")?.value).toBe("open");
    expect(stats.find((s) => s.label === "Core stack")?.value).toBe("Python · Vue 3 · Django");
    expect(stats.find((s) => s.label === "Experience")?.detail).toBe(
      "building and shipping products",
    );
  });
});
