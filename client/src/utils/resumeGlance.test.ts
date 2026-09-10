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
    expect(stack).toBe("Python · Vue 3 · FastAPI");
  });

  it("builds glance stats with availability when present", () => {
    const stats = buildGlanceStats(RESUME_FALLBACK);
    expect(stats).toHaveLength(4);
    expect(stats.find((s) => s.label === "Availability")?.value).toBe("open");
    expect(stats.find((s) => s.label === "Core stack")?.value).toBe("Python · Vue 3 · FastAPI");
    expect(stats.find((s) => s.label === "Experience")?.value).toBe("since 2017");
    expect(stats.find((s) => s.label === "Experience")?.detail).toBe(
      "platform sample since 2022",
    );
    expect(stats.find((s) => s.label === "Projects")?.detail).toBe(
      "one platform with live facets",
    );
  });
});
