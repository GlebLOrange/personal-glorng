import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { describe, expect, it } from "vitest";

import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";

describe("AdminFilterDropdown", () => {
  it("moves focus into the filter panel when opened", async () => {
    const wrapper = mount(AdminFilterDropdown, {
      props: { hasActiveFilters: true },
      slots: {
        default: '<button type="button">status</button>',
      },
      attachTo: document.body,
    });

    await wrapper.get("button").trigger("click");
    await nextTick();

    const dialog = document.querySelector('[role="dialog"][aria-label="filters"]');
    expect(dialog).toBeTruthy();
    expect(dialog?.contains(document.activeElement)).toBe(true);

    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    await nextTick();
    expect(document.querySelector('[role="dialog"]')).toBeNull();

    wrapper.unmount();
  });
});
