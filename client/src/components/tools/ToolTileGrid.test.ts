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

describe("ToolTileGrid", () => {
  it("shows a section count and opens in-app tools in place", () => {
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
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a class="page-tile" :href="to"><slot /></a>',
          },
        },
      },
    });

    expect(wrapper.get("h2").text()).toContain("utilities");
    expect(wrapper.get("h2").text()).toContain("1 tool");
    expect(wrapper.get("a").attributes("href")).toBe("/tools/calculator");
    expect(wrapper.get("a").attributes("target")).toBeUndefined();
    expect(wrapper.text()).not.toContain("short description");
  });

  it("shows a tile hint for ambiguous tool names only", () => {
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
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a class="page-tile" :href="to"><slot /></a>',
          },
        },
      },
    });

    expect(wrapper.text()).toContain("Check uptime, latency, SSL, and DNS.");
    expect(wrapper.text()).not.toContain("catalog blurb should stay hidden");
    expect(wrapper.text()).not.toContain("short description");
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
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a class="page-tile" :href="to"><slot /></a>',
          },
        },
      },
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
});
