import { mount, type VueWrapper } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import AdminTabBar from "@/components/admin/AdminTabBar.vue";

const tabs = [
  { id: "queue", label: "queue" },
  { id: "intakes", label: "intakes" },
  { id: "sync", label: "sync" },
];

function mountTabBar(activeTab = "queue"): VueWrapper {
  return mount(AdminTabBar, {
    attachTo: document.body,
    props: {
      tabs,
      modelValue: activeTab,
    },
  });
}

describe("AdminTabBar", () => {
  it("exposes tab semantics", () => {
    const wrapper = mountTabBar();

    expect(wrapper.get('[role="tablist"]').attributes("aria-label")).toBe("Admin sections");
    expect(wrapper.findAll('[role="tab"]')).toHaveLength(3);
    expect(wrapper.get('[role="tab"]').attributes("aria-selected")).toBe("true");
    expect(wrapper.get('[role="tab"]').attributes("tabindex")).toBe("0");

    wrapper.unmount();
  });

  it("supports arrow and boundary key navigation", async () => {
    const wrapper = mountTabBar();
    const firstTab = wrapper.findAll<HTMLButtonElement>('[role="tab"]')[0];

    await firstTab.trigger("keydown", { key: "ArrowRight" });
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual(["intakes"]);

    await wrapper.findAll<HTMLButtonElement>('[role="tab"]')[1].trigger("keydown", { key: "End" });
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual(["sync"]);

    await wrapper.findAll<HTMLButtonElement>('[role="tab"]')[2].trigger("keydown", { key: "Home" });
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual(["queue"]);

    wrapper.unmount();
  });
});
