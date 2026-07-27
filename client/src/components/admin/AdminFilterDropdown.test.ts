import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { describe, expect, it, vi } from "vitest";

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

    await nextTick();
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

    const trigger = wrapper.get('button[aria-haspopup="dialog"]');
    const closedWidth = trigger.element.offsetWidth;
    // Floor is the longest dropdown label ("not completed"), not an arbitrary min-w-40.
    expect(closedWidth).toBeGreaterThan(0);
    expect(trigger.element.style.minWidth).toMatch(/^\d+px$/);

    await trigger.trigger("click");
    await nextTick();
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

    const dialog = document.querySelector(
      '[role="dialog"][aria-label="filters"]',
    ) as HTMLElement | null;
    expect(dialog).toBeTruthy();
    // Trigger keeps a stable size when the panel opens.
    expect(trigger.element.offsetWidth).toBe(closedWidth);
    // Panel is at least the trigger bar; may grow for longer chip labels.
    expect(dialog!.offsetWidth).toBeGreaterThanOrEqual(trigger.element.offsetWidth);

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

  it("keeps trigger width floored to the longest option label", async () => {
    const wrapper = mount(AdminFilterDropdown, {
      props: {
        optionLabels: ["pending", "not completed", "cancelled"],
        activeLabel: "pending",
      },
      slots: {
        chips: {
          components: { AdminFilterChip },
          template: `
            <AdminFilterChip label="pending" />
            <AdminFilterChip label="not completed" />
            <AdminFilterChip label="cancelled" />
          `,
        },
      },
      attachTo: document.body,
    });

    await nextTick();
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

    const trigger = wrapper.get('button[aria-haspopup="dialog"]');
    const withShort = trigger.element.offsetWidth;

    await wrapper.setProps({ activeLabel: undefined });
    await nextTick();
    expect(trigger.element.offsetWidth).toBe(withShort);

    await wrapper.setProps({ activeLabel: "not completed" });
    await nextTick();
    expect(trigger.element.offsetWidth).toBe(withShort);

    wrapper.unmount();
  });

  it("anchors the teleported panel to the trigger width and viewport position", async () => {
    const wrapper = mount(AdminFilterDropdown, {
      props: { hasActiveFilters: true },
      slots: {
        chips: {
          components: { AdminFilterChip },
          template: '<AdminFilterChip label="warning" />',
        },
      },
      attachTo: document.body,
    });

    const trigger = wrapper.get('button[aria-haspopup="dialog"]').element as HTMLButtonElement;
    vi.spyOn(trigger, "getBoundingClientRect").mockReturnValue({
      x: 267,
      y: 370,
      top: 370,
      right: 555,
      bottom: 415,
      left: 267,
      width: 288,
      height: 45,
      toJSON: () => ({}),
    });

    await wrapper.get('button[aria-haspopup="dialog"]').trigger("click");
    await nextTick();
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

    const dialog = document.querySelector(
      '[role="dialog"][aria-label="filters"]',
    ) as HTMLElement | null;
    expect(dialog).toBeTruthy();
    expect(dialog!.style.top).toBe("419px");
    expect(dialog!.style.left).toBe("267px");
    // Never narrower than the filter bar.
    expect(dialog!.style.minWidth).toBe("288px");

    wrapper.unmount();
  });
});
