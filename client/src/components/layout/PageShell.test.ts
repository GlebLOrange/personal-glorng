import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import PageShell from "@/components/layout/PageShell.vue";

const stubs = {
  PageChrome: {
    props: ["description"],
    template: `<div data-testid="chrome" :data-description="description ?? ''" />`,
  },
  PinnedToolsRow: { template: '<div data-testid="pinned" />' },
};

describe("PageShell", () => {
  it("forwards description to PageChrome when set", () => {
    const wrapper = mount(PageShell, {
      props: {
        title: "news",
        breadcrumbs: [{ label: "news" }],
        description: "Curated digest from scheduled RSS ingest.",
      },
      global: { stubs },
      slots: { default: "<div>body</div>" },
    });

    expect(wrapper.get('[data-testid="chrome"]').attributes("data-description")).toBe(
      "Curated digest from scheduled RSS ingest.",
    );
    expect(wrapper.find('[data-testid="page-description"]').exists()).toBe(false);
  });

  it("omits chrome description when unset", () => {
    const wrapper = mount(PageShell, {
      props: {
        title: "tools",
        breadcrumbs: [{ label: "tools" }],
      },
      global: { stubs },
      slots: { default: "<div>body</div>" },
    });

    expect(wrapper.get('[data-testid="chrome"]').attributes("data-description")).toBe("");
  });
});
