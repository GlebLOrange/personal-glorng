import { describe, expect, it } from "vitest";

import {
  ADMIN_HUB_DEMO_SLUGS,
  ADMIN_HUB_SERVICE_SLUGS,
  PLATFORM_SERVICES,
  groupAdminHub,
  groupServicesByCategory,
} from "@/platform/services";

const HUB_SLUGS = [
  "news",
  "news-sources",
  "email",
  "tasks",
  "ai-chat",
  "url-shortener",
  "weather",
  "recipes",
  "health-checker",
  "feedback",
  "audit",
  "app-logs",
  "search",
  "api-docs",
  "db-maintenance",
] as const;

const OPERATIONS_SLUGS = [
  "feedback",
  "audit",
  "app-logs",
  "search",
  "api-docs",
  "db-maintenance",
] as const;

describe("groupAdminHub", () => {
  it("returns sentence-case sections in slug order without changing categories", () => {
    const services = PLATFORM_SERVICES.filter((service) =>
      ADMIN_HUB_SERVICE_SLUGS.has(service.slug),
    );
    const categoriesBefore = new Map(services.map((service) => [service.slug, service.category]));
    const sections = groupAdminHub([...services].reverse());

    expect(sections.map((section) => section.label)).toEqual([
      "Content",
      "Productivity",
      "Utilities",
      "Operations",
    ]);
    expect(sections.map((section) => section.services.map((service) => service.slug))).toEqual([
      ["news", "news-sources"],
      ["email", "tasks"],
      ["ai-chat", "url-shortener", "weather", "recipes", "health-checker"],
      [...OPERATIONS_SLUGS],
    ]);

    for (const section of sections) {
      for (const service of section.services) {
        expect(service.category).toBe(categoriesBefore.get(service.slug));
        expect(service).toBe(services.find((item) => item.slug === service.slug));
      }
    }

    const utilities = sections.find((section) => section.label === "Utilities");
    expect(utilities?.services.find((service) => service.slug === "url-shortener")?.category).toBe(
      "content",
    );
    expect(utilities?.services.find((service) => service.slug === "recipes")?.category).toBe(
      "content",
    );
    expect(utilities?.services.find((service) => service.slug === "weather")?.category).toBe(
      "utilities",
    );

    const byCategory = groupServicesByCategory(services);
    expect(
      byCategory.find((section) => section.category === "content")?.services.map((s) => s.slug),
    ).toEqual(expect.arrayContaining(["url-shortener", "recipes", "news"]));
    expect(
      byCategory.find((section) => section.category === "utilities")?.services.map((s) => s.slug),
    ).toContain("weather");
  });

  it("omits a section that has no services", () => {
    const services = PLATFORM_SERVICES.filter(
      (service) => service.slug === "news" || service.slug === "feedback",
    );
    const sections = groupAdminHub(services);

    expect(sections.map((section) => section.label)).toEqual(["Content", "Operations"]);
    expect(groupAdminHub([])).toEqual([]);
  });

  it("exports the hub slug set and a demo set that excludes health, recipes, and operations", () => {
    expect(ADMIN_HUB_SERVICE_SLUGS).toEqual(new Set(HUB_SLUGS));
    expect(ADMIN_HUB_DEMO_SLUGS).toEqual(new Set(["ai-chat", "url-shortener", "weather"]));
    expect(ADMIN_HUB_DEMO_SLUGS.has("health-checker")).toBe(false);
    expect(ADMIN_HUB_DEMO_SLUGS.has("recipes")).toBe(false);
    for (const slug of OPERATIONS_SLUGS) {
      expect(ADMIN_HUB_DEMO_SLUGS.has(slug)).toBe(false);
    }
  });
});
