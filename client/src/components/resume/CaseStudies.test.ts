import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import CaseStudies from "@/components/resume/CaseStudies.vue";
import type { Project } from "@/types";

const projects: Project[] = [
  {
    slug: "ledger",
    name: "Ledger",
    description: "Tracks invoices for a small studio.",
    tech: ["Python"],
    url: "https://example.com/ledger",
    problem: "Late invoices.",
    approach: "Nightly sync.",
    result: "Paid faster.",
  },
  {
    slug: "queue",
    name: "Queue",
    description: "Buffers webhook deliveries.",
    tech: ["Redis"],
    url: "https://example.com/queue",
    problem: "Dropped events.",
    approach: "Retry with backoff.",
    result: "No lost webhooks.",
  },
];

describe("CaseStudies", () => {
  it("shows proof (problem / approach / result) without a click", () => {
    const wrapper = mount(CaseStudies, {
      props: { projects },
      global: { stubs: { RouterLink: { template: "<a><slot /></a>" } } },
    });
    const rows = wrapper.findAll("article");
    expect(rows).toHaveLength(projects.length);

    projects.forEach((project, index) => {
      const row = rows[index];
      expect(row, project.name).toBeDefined();
      if (!row) return;

      expect(row.get("h3").text()).toBe(project.name);
      expect(row.text()).toContain(project.description);
      expect(row.text()).toContain(project.problem ?? "");
      expect(row.text()).toContain(project.result ?? "");
      expect(row.text()).toContain("live site");
      expect(row.text()).not.toContain(project.url);
    });
  });
});
