import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { describe, expect, it } from "vitest";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
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

  it("does not grow root height when the panel opens", async () => {
    const wrapper = mount(AdminFilterDropdown, {
      props: { hasActiveFilters: true },
      slots: {
        chips: {
          components: { AdminFilterChip },
          template: `
            <AdminFilterChip label="draft" />
            <AdminFilterChip label="published" />
            <AdminFilterChip label="archived" />
          `,
        },
      },
      attachTo: document.body,
    });

    const root = wrapper.element as HTMLElement;
    const closedHeight = root.offsetHeight;

    await wrapper.get('button[aria-haspopup="dialog"]').trigger("click");
    await nextTick();

    expect(document.querySelector('[role="dialog"][aria-label="filters"]')).toBeTruthy();
    expect(root.offsetHeight).toBe(closedHeight);

    wrapper.unmount();
  });

  it("keeps a stable mid width open and closed", async () => {
    const wrapper = mount(AdminFilterDropdown, {
      props: { hasActiveFilters: true },
      slots: {
        chips: {
          components: { AdminFilterChip },
          template: `
            <AdminFilterChip label="pending" />
            <AdminFilterChip label="not completed" />
          `,
        },
      },
      attachTo: document.body,
    });

    const trigger = wrapper.get('button[aria-haspopup="dialog"]');
    const closedWidth = trigger.element.offsetWidth;

    await trigger.trigger("click");
    await nextTick();
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

    const dialog = document.querySelector(
      '[role="dialog"][aria-label="filters"]',
    ) as HTMLElement | null;
    expect(dialog).toBeTruthy();
    // Fixed mid column — trigger does not jump when the panel opens.
    expect(trigger.element.offsetWidth).toBe(closedWidth);
    expect(dialog!.offsetWidth).toBe(trigger.element.offsetWidth);

    const chip = dialog!.querySelector("button[aria-pressed]") as HTMLButtonElement | null;
    const clear = Array.from(dialog!.querySelectorAll("button")).find(
      (btn) => btn.textContent?.trim() === "clear",
    ) as HTMLButtonElement | undefined;
    expect(chip).toBeTruthy();
    expect(clear).toBeTruthy();
    expect(clear!.offsetWidth).toBe(chip!.offsetWidth);
    // Same chip geometry (not tall BaseButton h-10).
    expect(clear!.offsetHeight).toBe(chip!.offsetHeight);

    wrapper.unmount();
  });

  it("keeps the panel open when clicking inside a teleported panel", async () => {
    const wrapper = mount(AdminFilterDropdown, {
      props: { hasActiveFilters: true },
      slots: {
        chips: {
          components: { AdminFilterChip },
          template: '<AdminFilterChip label="archived" />',
        },
      },
      attachTo: document.body,
    });

    await wrapper.get('button[aria-haspopup="dialog"]').trigger("click");
    await nextTick();

    const dialog = document.querySelector(
      '[role="dialog"][aria-label="filters"]',
    ) as HTMLElement | null;
    expect(dialog).toBeTruthy();

    dialog!.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    await nextTick();
    expect(document.querySelector('[role="dialog"][aria-label="filters"]')).toBeTruthy();

    document.body.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    await nextTick();
    expect(document.querySelector('[role="dialog"]')).toBeNull();

    wrapper.unmount();
  });
});
