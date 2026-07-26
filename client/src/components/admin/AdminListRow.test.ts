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
});
