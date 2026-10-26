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
  it("maps public slugs into utils (tabs) then content (tiles)", () => {
    const sections = groupServicesForToolsPage(publicToolsAsServices());
    expect(sections.map((s) => s.category)).toEqual(["utils", "content"]);
    expect(sections[0]?.services.map((t) => t.slug)).toEqual([
      "weather",
      "calculator",
      "password-generator",
      "qr-generator",
    ]);
    expect(sections[1]?.services.map((t) => t.slug)).toEqual(["recipes", "url-shortener"]);
  });

  it("places extras and admin hub tools into utils / content / server", () => {
    const extras = PLATFORM_SERVICES.filter((tool) => TOOLS_PAGE_EXTRA_SLUGS.has(tool.slug));
    const hub = PLATFORM_SERVICES.filter((tool) =>
      ["email", "ai-chat", "health-checker", "news", "news-sources", "feedback", "audit"].includes(
        tool.slug,
      ),
    );
    const sections = groupServicesForToolsPage([
      ...publicToolsAsServices(),
      ...extras,
      ...hub,
    ]);
    expect(sections.map((s) => s.category)).toEqual(["utils", "content", "server"]);
    expect(sections.find((s) => s.category === "utils")?.services.map((t) => t.slug)).toEqual([
      "weather",
      "calculator",
      "password-generator",
      "qr-generator",
      "vid-download",
      "email",
    ]);
    expect(sections.find((s) => s.category === "content")?.services.map((t) => t.slug)).toEqual([
      "recipes",
      "tasks",
      "expenses",
      "url-shortener",
      "file-share",
      "data-extract",
      "ai-chat",
      "health-checker",
      "news",
      "news-sources",
    ]);
    expect(sections.find((s) => s.category === "server")?.services.map((t) => t.slug)).toEqual([
      "feedback",
      "audit",
    ]);
    expect(PLATFORM_SERVICES.find((t) => t.slug === "tasks")?.category).toBe("productivity");
    expect(PLATFORM_SERVICES.find((t) => t.slug === "weather")?.category).toBe("utilities");
  });

  it("dedupes by slug when the same tool appears twice", () => {
    const weather = PLATFORM_SERVICES.find((t) => t.slug === "weather")!;
    const sections = groupServicesForToolsPage([weather, weather]);
    expect(sections[0]?.services).toHaveLength(1);
  });

  it("skips chips for tab slugs; demo/yours for content tiles", () => {
    expect(toolsPageChipForSlug("weather")).toBeUndefined();
    expect(toolsPageChipForSlug("calculator")).toBeUndefined();
    expect(toolsPageChipForSlug("recipes")).toBe("demo");
    expect(toolsPageChipForSlug("url-shortener")).toBe("demo");
    expect(toolsPageChipForSlug("tasks")).toBe("yours");
    expect(toolsPageChipForSlug("data-extract")).toBe("yours");
    expect(toolsPageChipForSlug("news")).toBeUndefined();
    expect(toolsPageGroupForSlug("file-share")).toBe("content");
    expect(toolsPageGroupForSlug("vid-download")).toBe("utils");
    expect(toolsPageGroupForSlug("feedback")).toBe("server");
  });
});
