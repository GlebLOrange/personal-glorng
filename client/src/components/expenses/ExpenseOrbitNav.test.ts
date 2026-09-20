import { mount, type VueWrapper } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ExpenseOrbitNav from "@/components/expenses/ExpenseOrbitNav.vue";

const tabs = [
  { id: "expenses", label: "expenses" },
  { id: "transactions", label: "transactions" },
  { id: "analytics", label: "analytics" },
];

function mountOrbit(activeTab = "expenses"): VueWrapper {
  return mount(ExpenseOrbitNav, {
    attachTo: document.body,
    props: {
      tabs,
      modelValue: activeTab,
      panelIdPrefix: "expenses-tab",
      ariaLabel: "expense sections",
    },
  });
}

describe("ExpenseOrbitNav", () => {
  it("exposes tablist semantics with planet buttons", () => {
    const wrapper = mountOrbit();

    expect(wrapper.get('[role="tablist"]').attributes("aria-label")).toBe("expense sections");
    expect(wrapper.findAll('[role="tab"]')).toHaveLength(3);
    expect(wrapper.get('[role="tab"]').attributes("aria-selected")).toBe("true");
    expect(wrapper.get('[role="tab"]').attributes("tabindex")).toBe("0");
    expect(wrapper.get('[role="tab"]').attributes("aria-controls")).toBe(
      "expenses-tab-panel-expenses",
    );
    expect(wrapper.get('[role="tab"]').attributes("id")).toBe("expenses-tab-tab-expenses");
    expect(wrapper.get("#expenses-tab-tab-expenses").text()).toContain("E");
    expect(wrapper.text()).toContain("expenses");

    wrapper.unmount();
  });

  it("scales the selected planet with accent wash", () => {
    const wrapper = mountOrbit("transactions");
    const selected = wrapper.get("#expenses-tab-tab-transactions");
    expect(selected.classes()).toContain("scale-110");
    expect(selected.classes()).toContain("border-accent-blue/40");
    expect(selected.classes()).toContain("bg-accent-blue/15");

    const idle = wrapper.get("#expenses-tab-tab-expenses");
    expect(idle.classes()).toContain("border-transparent");
    expect(idle.classes()).toContain("bg-surface-dark/90");
    expect(idle.classes()).not.toContain("scale-110");

    wrapper.unmount();
  });

  it("renders a decorative NASA Earth backdrop", () => {
    const wrapper = mountOrbit();
    const img = wrapper.get("img");
    expect(img.attributes("src")).toBe("/expenses/orbit-earth.webp");
    expect(img.attributes("alt")).toBe("");
    expect(img.attributes("aria-hidden")).toBe("true");
    expect(img.attributes("decoding")).toBe("async");
    expect(img.attributes("fetchpriority")).toBe("low");
    expect(wrapper.text()).toContain("Background: NASA Earth from orbit (public domain).");

    wrapper.unmount();
  });

  it("supports arrow and boundary key navigation", async () => {
    const wrapper = mountOrbit();
    const firstTab = wrapper.findAll<HTMLButtonElement>('[role="tab"]')[0];

    await firstTab.trigger("keydown", { key: "ArrowRight" });
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual(["transactions"]);

    await wrapper.findAll<HTMLButtonElement>('[role="tab"]')[1].trigger("keydown", { key: "End" });
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual(["analytics"]);

    await wrapper.findAll<HTMLButtonElement>('[role="tab"]')[2].trigger("keydown", {
      key: "Home",
    });
    expect(wrapper.emitted("update:modelValue")?.at(-1)).toEqual(["expenses"]);

    wrapper.unmount();
  });

  it("renders a right-aligned end slot outside the tablist", () => {
    const wrapper = mount(ExpenseOrbitNav, {
      props: {
        tabs: [{ id: "expenses", label: "expenses" }],
        modelValue: "expenses",
      },
      slots: {
        end: '<button type="button" aria-label="export csv">export</button>',
      },
    });

    const tablist = wrapper.get('[role="tablist"]');
    expect(tablist.find('[aria-label="export csv"]').exists()).toBe(false);
    expect(wrapper.get('[aria-label="export csv"]').exists()).toBe(true);
    expect(wrapper.html()).toContain("ml-auto");

    wrapper.unmount();
  });
});
