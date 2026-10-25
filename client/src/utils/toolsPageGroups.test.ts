import { describe, expect, it } from "vitest";

import {
  PLATFORM_SERVICES,
  publicToolsAsServices,
  TOOLS_PAGE_EXTRA_SLUGS,
} from "@/platform/services";
import {
  groupServicesForToolsPage,
  toolsPageChipForSlug,
  toolsPageGroupForSlug,
} from "@/utils/toolsPageGroups";

describe("toolsPageGroups", () => {
  it("maps public slugs into Everyday then Content order", () => {
    const sections = groupServicesForToolsPage(publicToolsAsServices());
    expect(sections.map((s) => s.category)).toEqual(["everyday", "content"]);
    expect(sections[0]?.services.map((t) => t.slug)).toEqual([
      "weather",
      "calculator",
      "password-generator",
      "qr-generator",
    ]);
    expect(sections[1]?.services.map((t) => t.slug)).toEqual(["url-shortener", "recipes"]);
  });

  it("places Work and Builders extras without changing platform categories", () => {
    const extras = PLATFORM_SERVICES.filter((tool) => TOOLS_PAGE_EXTRA_SLUGS.has(tool.slug));
    const sections = groupServicesForToolsPage([...publicToolsAsServices(), ...extras]);
    expect(sections.map((s) => s.category)).toEqual([
      "everyday",
      "content",
      "work",
      "builders",
    ]);
    expect(sections.find((s) => s.category === "work")?.services.map((t) => t.slug)).toEqual([
      "tasks",
      "expenses",
      "file-share",
    ]);
    expect(sections.find((s) => s.category === "builders")?.services.map((t) => t.slug)).toEqual([
      "vid-download",
      "data-extract",
    ]);
    expect(PLATFORM_SERVICES.find((t) => t.slug === "tasks")?.category).toBe("productivity");
    expect(PLATFORM_SERVICES.find((t) => t.slug === "weather")?.category).toBe("utilities");
  });

  it("returns demo chips for public tools and yours for Work/Builders", () => {
    expect(toolsPageChipForSlug("weather")).toBe("demo");
    expect(toolsPageChipForSlug("recipes")).toBe("demo");
    expect(toolsPageChipForSlug("tasks")).toBe("yours");
    expect(toolsPageChipForSlug("data-extract")).toBe("yours");
    expect(toolsPageChipForSlug("news")).toBeUndefined();
    expect(toolsPageGroupForSlug("file-share")).toBe("work");
  });
});
