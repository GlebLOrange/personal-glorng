import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import CaseStudies from "@/components/resume/CaseStudies.vue";
import type { Project } from "@/types";

vi.mock("@/composables/useColorTheme", () => ({
  colorThemeResolved: { value: "dark" },
}));

const projects: Project[] = [
  {
    slug: "cookie-auth-csrf",
    name: "cookie auth & CSRF",
    description: "Browser sessions need CSRF without breaking Bearer clients.",
    tech: ["FastAPI", "cookies"],
    url: "https://gleblorange.github.io/personal-glorng/reference/security.html",
    problem: "Cookie auth CSRF risk.",
    approach: "Origin checks on mutating /api.",
    result: "Bad Origin rejected in production.",
  },
  {
    slug: "ssrf-safe-fetch",
    name: "SSRF-safe outbound fetch",
    description: "Server-side HTTP must not reach private networks.",
    tech: ["Python", "httpx"],
    url: "https://github.com/GlebLOrange/personal-glorng/blob/main/server/app/core/url_safety.py",
    problem: "SNI fails after DNS pin.",
    approach: "Connect to IP with Host + sni_hostname.",
    result: "Fail-closed public fetch with unit coverage.",
  },
];

describe("CaseStudies", () => {
  it("renders scan-first tiles with art, outcome, case fields, stack, and labelled links", () => {
    const wrapper = mount(CaseStudies, {
      props: { projects },
      global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } },
    });

    expect(wrapper.findAll("details")).toHaveLength(0);
    const cards = wrapper.findAll("article");
    expect(cards).toHaveLength(projects.length);

    const first = cards[0]!;
    const art = first.get("img");
    expect(art.attributes("alt")).toBe("");
    expect(art.attributes("src")).toBe("/portfolio/cookie-auth-csrf-dark.svg");
    expect(first.text()).toContain("cookie auth & CSRF");
    expect(first.text()).toContain(projects[0]!.description);
    expect(first.text()).toContain("problem");
    expect(first.text()).toContain(projects[0]!.problem!);
    expect(first.text()).toContain("approach");
    expect(first.text()).toContain("result");
    expect(first.text()).toContain("FastAPI");
    expect(first.text()).toContain("live site");
    expect(first.text()).not.toContain(projects[0]!.url);

    const second = cards[1]!;
    expect(second.get("img").attributes("src")).toBe("/portfolio/ssrf-safe-fetch-dark.svg");
    expect(second.text()).toContain("repository");
    expect(second.text()).not.toContain(projects[1]!.url);
  });

  it("uses fallback art for unknown project slugs", () => {
    const wrapper = mount(CaseStudies, {
      props: {
        projects: [
          {
            slug: "unknown-system",
            name: "Unknown",
            description: "A new case study.",
            tech: ["Vue"],
            url: "/tools",
          },
        ],
      },
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: '<a :href="to"><slot /></a>',
          },
        },
      },
    });

    expect(wrapper.get("img").attributes("src")).toBe("/portfolio/fallback-dark.svg");
    expect(wrapper.text()).toContain("open");
  });
});
