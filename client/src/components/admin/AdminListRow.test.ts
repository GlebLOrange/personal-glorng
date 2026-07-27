/**
 * @vitest-environment happy-dom
 */
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import AdminListRow from "@/components/admin/AdminListRow.vue";

describe("AdminListRow", () => {
  it("exposes a primary open button when nestedInteractive", async () => {
    const wrapper = mount(AdminListRow, {
      props: { interactive: true, nestedInteractive: true },
      slots: {
        primary: "Feedback theme",
        actions: '<button type="button">edit</button>',
      },
    });

    const openBtn = wrapper.get("[data-admin-list-open]");
    expect(openBtn.text()).toContain("Feedback theme");
    expect(wrapper.attributes("role")).toBeUndefined();
    expect(wrapper.attributes("tabindex")).toBeUndefined();

    await openBtn.trigger("click");
    expect(wrapper.emitted("click")).toHaveLength(1);
  });

  it("keeps the row itself activatable when not nestedInteractive", async () => {
    const wrapper = mount(AdminListRow, {
      props: { interactive: true, expandable: true, expanded: false },
      slots: { primary: "Audit action" },
    });

    expect(wrapper.attributes("role")).toBe("button");
    expect(wrapper.attributes("tabindex")).toBe("0");
    expect(wrapper.attributes("aria-expanded")).toBe("false");
    expect(wrapper.find("[data-admin-list-open]").exists()).toBe(false);

    await wrapper.trigger("keydown", { key: "Enter" });
    expect(wrapper.emitted("click")?.length).toBeGreaterThanOrEqual(1);
  });

  it("applies status ring only when expanded", () => {
    const statusClass = "text-status-success bg-status-success/15 border-status-success/30";

    const idle = mount(AdminListRow, {
      props: { statusClass, expandable: true, expanded: false },
      slots: { primary: "auth.login_success" },
    });
    expect(idle.classes()).not.toContain("!ring-status-success/50");
    expect(idle.classes()).toContain("hover:!ring-status-success/50");

    const active = mount(AdminListRow, {
      props: { statusClass, expandable: true, expanded: true },
      slots: { primary: "auth.login_success" },
    });
    expect(active.classes()).toContain("!ring-status-success/50");
  });

  it("uses accent and neutral status rings for news source tones", () => {
    const enabled = mount(AdminListRow, {
      props: {
        statusClass: "text-accent-blue bg-accent-blue/15 border-accent-blue/30",
        interactive: true,
      },
      slots: { primary: "DW" },
    });
    expect(enabled.classes()).toContain("hover:!ring-accent-blue/50");

    const disabled = mount(AdminListRow, {
      props: {
        statusClass: "bg-surface-border text-surface-mid border-surface-border",
        interactive: true,
      },
      slots: { primary: "Al Jazeera" },
    });
    expect(disabled.classes()).toContain("hover:!ring-surface-border");
  });

  it("keeps the main row at control height", () => {
    const wrapper = mount(AdminListRow, {
      props: { interactive: true },
      slots: { primary: "plan sprint" },
    });
    const header = wrapper.find("[data-admin-list-header]");
    expect(header.classes()).toContain("h-10");
  });
});
