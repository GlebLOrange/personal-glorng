import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ToolTileGrid from "@/components/tools/ToolTileGrid.vue";
import type { PlatformService } from "@/platform/services";

function service(
  overrides: Partial<PlatformService> & Pick<PlatformService, "slug">,
): PlatformService {
  return {
    name: overrides.slug,
    category: "utilities",
    categoryLabel: "utilities",
    description: "short description",
    apiPrefix: "/api",
    adminRoute: `/tools/${overrides.slug}`,
    icon: "square",
    capabilities: [],
    external: false,
    ...overrides,
  };
}

const routerLinkStub = {
  name: "RouterLink",
  props: ["to"],
  template: '<a class="page-tile" :href="to"><slot /></a>',
};

describe("ToolTileGrid", () => {
  it("shows a section count and opens in-app tools in place by default", () => {
    const wrapper = mount(ToolTileGrid, {
      props: {
        sections: [
          {
            category: "utilities",
            label: "utilities",
            services: [service({ slug: "calculator", name: "calculator" })],
          },
        ],
      },
      global: { stubs: { RouterLink: routerLinkStub } },
    });

    expect(wrapper.get("h2").text()).toContain("utilities");
    expect(wrapper.get("h2").text()).toContain("1 tool");
    expect(wrapper.get("h2").text()).toMatch(/\b1\b/);
    expect(wrapper.get("a").attributes("href")).toBe("/tools/calculator");
    expect(wrapper.get("a").attributes("target")).toBeUndefined();
    expect(wrapper.text()).not.toContain("short description");
    expect(wrapper.text()).not.toContain("Do a quick calculation.");
  });

  it("shows a tile hint for ambiguous tool names only in the default presentation", () => {
    const wrapper = mount(ToolTileGrid, {
      props: {
        sections: [
          {
            category: "utilities",
            label: "utilities",
            services: [
              service({
                slug: "health-checker",
                name: "health checker",
                description: "catalog blurb should stay hidden",
              }),
              service({ slug: "calculator", name: "calculator" }),
            ],
          },
        ],
      },
      global: { stubs: { RouterLink: routerLinkStub } },
    });

    expect(wrapper.text()).toContain("Check uptime, latency, SSL, and DNS.");
    expect(wrapper.text()).not.toContain("catalog blurb should stay hidden");
    expect(wrapper.text()).not.toContain("short description");
  });

  it("public presentation shows blurbs, hides visible counts, and keeps one full-row link", () => {
    const wrapper = mount(ToolTileGrid, {
      props: {
        presentation: "public",
        sections: [
          {
            category: "utilities",
            label: "utilities",
            services: [
              service({ slug: "weather", name: "weather" }),
              service({ slug: "calculator", name: "calculator" }),
            ],
          },
        ],
      },
      global: { stubs: { RouterLink: routerLinkStub } },
    });

    const heading = wrapper.get("h2");
    expect(heading.text()).toContain("utilities");
    expect(heading.text()).toContain("2 tools");
    expect(heading.find("[aria-hidden=\"true\"]").exists()).toBe(false);

    const links = wrapper.findAll("a.page-tile");
    expect(links).toHaveLength(2);
    expect(wrapper.text()).toContain("Check the weather and local time.");
    expect(wrapper.text()).toContain("Do a quick calculation.");
    expect(wrapper.find(".page-tile-chevron").classes()).toContain("pointer-events-none");
    expect(wrapper.get('[data-presentation="public"]').exists()).toBe(true);
  });

  it("hides a one-tool h3 category heading under a parent section", () => {
    const wrapper = mount(ToolTileGrid, {
      props: {
        categoryHeading: "h3",
        sections: [
          {
            category: "content",
            label: "content",
            services: [service({ slug: "file-share", name: "file share", category: "content" })],
          },
        ],
      },
      global: { stubs: { RouterLink: routerLinkStub } },
    });

    expect(wrapper.find("h3").exists()).toBe(false);
    expect(wrapper.find("h2").exists()).toBe(false);
    expect(wrapper.text()).toContain("file share");
  });

  it("marks external tools as a new tab without a catalog subtitle", () => {
    const wrapper = mount(ToolTileGrid, {
      props: {
        sections: [
          {
            category: "operations",
            label: "operations",
            services: [
              service({
                slug: "api-docs",
                name: "api docs",
                external: true,
                adminRoute: "https://example.test/docs",
                description: "openapi reference",
              }),
            ],
          },
        ],
      },
    });

    const link = wrapper.get("a");
    expect(link.attributes("href")).toBe("https://example.test/docs");
    expect(link.attributes("target")).toBe("_blank");
    expect(link.attributes("rel")).toBe("noopener noreferrer");
    expect(link.text()).not.toContain("openapi reference");
    expect(link.text()).toContain("opens in a new tab");
  });

  it("admin presentation shows Label · count, a clamped description, and a demo chip", () => {
    const wrapper = mount(ToolTileGrid, {
      props: {
        presentation: "admin",
        resolveRoute: () => "/should-not-use",
        tileChip: () => "yours" as const,
        sections: [
          {
            category: "utilities",
            label: "Utilities",
            services: [
              service({
                slug: "weather",
                name: "weather",
                description: "weather lookup, saved locations, and local time",
                adminRoute: "/weather",
              }),
              service({
                slug: "recipes",
                name: "recipes",
                description: "personal recipe book and food notes",
                adminRoute: "/recipes",
              }),
              service({
                slug: "health-checker",
                name: "health checker",
                description: "monitor website and api uptime, latency, ssl, and dns",
                adminRoute: "/health-checker",
              }),
            ],
          },
          {
            category: "operations",
            label: "Operations",
            services: [
              service({
                slug: "feedback",
                name: "feedback",
                category: "operations",
                description: "read visitor feedback messages",
                adminRoute: "/admin/feedback",
              }),
              service({
                slug: "api-docs",
                name: "api docs",
                category: "operations",
                external: true,
                adminRoute: "https://example.test/docs",
                description: "swagger api documentation",
              }),
            ],
          },
        ],
      },
      global: { stubs: { RouterLink: routerLinkStub } },
    });

    const utilitiesHeading = wrapper.get("#utilities h2");
    expect(utilitiesHeading.get("[aria-hidden='true']").text()).toBe("Utilities · 3");
    expect(utilitiesHeading.findAll("[aria-hidden='true']")).toHaveLength(1);
    expect(wrapper.get("#operations h2").get("[aria-hidden='true']").text()).toBe("Operations · 2");

    const weather = wrapper.get("a[href='/weather']");
    const description = weather.get("p");
    expect(description.classes()).toContain("line-clamp-1");
    expect(description.text()).toBe("weather lookup, saved locations, and local time");
    expect(weather.text()).toContain("Demo");
    expect(weather.text()).not.toContain("yours");
    expect(weather.text()).not.toContain("Check the weather and local time.");

    expect(wrapper.get("a[href='/recipes']").text()).not.toContain("Demo");
    expect(wrapper.get("a[href='/health-checker']").text()).not.toContain("Demo");
    expect(wrapper.get("a[href='/admin/feedback']").text()).not.toContain("Demo");

    const inApp = wrapper.findAllComponents({ name: "RouterLink" });
    expect(inApp.map((link) => link.props("to"))).toEqual([
      "/weather",
      "/recipes",
      "/health-checker",
      "/admin/feedback",
    ]);

    const docs = wrapper.get("a[href='https://example.test/docs']");
    expect(docs.attributes("target")).toBe("_blank");
    expect(docs.attributes("rel")).toBe("noopener noreferrer");
    expect(inApp.map((link) => link.props("to"))).not.toContain("https://example.test/docs");

    const chips = wrapper.get("nav[aria-label='Sections']").findAll("a");
    expect(chips.map((chip) => chip.attributes("href"))).toEqual(["#utilities", "#operations"]);
    expect(chips[0].classes()).toEqual(expect.arrayContaining(["h-11", "min-w-11"]));
    expect(wrapper.get("#utilities").classes()).toContain("scroll-mt-24");
  });

  it("omits the admin section chip row when only one section is present", () => {
    const wrapper = mount(ToolTileGrid, {
      props: {
        presentation: "admin",
        sections: [
          {
            category: "content",
            label: "Content",
            services: [
              service({
                slug: "news",
                name: "manage news",
                description: "curated worldwide news digest",
                adminRoute: "/admin/news",
              }),
            ],
          },
        ],
      },
      global: { stubs: { RouterLink: routerLinkStub } },
    });

    expect(wrapper.find("nav").exists()).toBe(false);
    expect(wrapper.get("#content h2").get("[aria-hidden='true']").text()).toBe("Content · 1");
  });
});
