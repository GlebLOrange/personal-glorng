import { mount, type VueWrapper } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import AdminTabBar from "@/components/admin/AdminTabBar.vue";

const tabs = [
  { id: "queue", label: "queue" },
  { id: "intakes", label: "intakes" },
  { id: "sync", label: "sync", icon: "sync" as const },
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

    expect(wrapper.get('[role="tablist"]').attributes("aria-label")).toBe("admin sections");
    expect(wrapper.findAll('[role="tab"]')).toHaveLength(3);
    expect(wrapper.get('[role="tab"]').attributes("aria-selected")).toBe("true");
    expect(wrapper.get('[role="tab"]').attributes("tabindex")).toBe("0");
    expect(wrapper.get('[role="tab"]').attributes("aria-controls")).toBe("admin-tab-panel-queue");
    expect(wrapper.get('[role="tab"]').attributes("id")).toBe("admin-tab-tab-queue");

    wrapper.unmount();
  });

  it("paints sync/refresh tabs with pale 1xx wash by default (not marketing violet)", () => {
    const wrapper = mount(AdminTabBar, {
      props: {
        modelValue: "sync",
        tabs: [
          { id: "queue", label: "queue" },
          { id: "sync", label: "sync", icon: "sync" },
          { id: "refresh", label: "refresh", icon: "refresh" },
        ],
      },
    });

    const syncTab = wrapper.get("#admin-tab-tab-sync");
    expect(syncTab.classes()).toContain("text-accent-blue");
    expect(syncTab.classes()).toContain("bg-accent-blue/15");
    expect(syncTab.classes()).toContain("border-accent-blue/40");
    expect(syncTab.classes()).not.toContain("text-accent-violet");

    const refreshTab = wrapper.get("#admin-tab-tab-refresh");
    expect(refreshTab.classes()).toContain("text-accent-blue");
    expect(refreshTab.classes()).toContain("bg-accent-blue/3");
    expect(refreshTab.classes()).not.toContain("text-accent-violet");
  });

  it("honors family=5xx critical wash when set on a tab", () => {
    const wrapper = mount(AdminTabBar, {
      props: {
        modelValue: "sync",
        tabs: [{ id: "sync", label: "sync", icon: "sync", family: "5xx" }],
      },
    });

    const syncTab = wrapper.get("#admin-tab-tab-sync");
    expect(syncTab.classes()).toContain("text-status-critical");
    expect(syncTab.classes()).toContain("bg-status-critical/15");
    expect(syncTab.classes()).toContain("border-status-critical/40");
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

  it("renders a right-aligned end slot outside the tablist", () => {
    const wrapper = mount(AdminTabBar, {
      props: {
        tabs: [{ id: "chat", label: "chat" }],
        modelValue: "chat",
      },
      slots: {
        end: '<button type="button" aria-label="setup help">?</button>',
      },
    });

    const tablist = wrapper.get('[role="tablist"]');
    expect(tablist.find('[aria-label="setup help"]').exists()).toBe(false);
    expect(wrapper.get('[aria-label="setup help"]').exists()).toBe(true);
    expect(wrapper.html()).toContain("ml-auto");

    wrapper.unmount();
  });
});
