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

    // jsdom often reports 0 scrollWidth/offsetWidth — seed the probe for min-width.
    const measure = wrapper.element.querySelector(
      '[aria-hidden="true"].pointer-events-none',
    ) as HTMLElement | null;
    expect(measure).toBeTruthy();
    Object.defineProperty(measure!, "scrollWidth", { configurable: true, get: () => 200 });
    for (const node of measure!.querySelectorAll<HTMLElement>(
      "button, input, select, textarea, label, span",
    )) {
      const label = node.textContent?.trim() ?? "";
      const width = label === "not completed" ? 180 : 120;
      Object.defineProperty(node, "scrollWidth", { configurable: true, get: () => width });
    }
    window.dispatchEvent(new Event("resize"));
    await nextTick();
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

    const trigger = wrapper.get('button[aria-haspopup="dialog"]');
    // Floor is the longest dropdown label ("not completed"), not an arbitrary min-w-40.
    expect(Number.parseFloat(trigger.element.style.minWidth)).toBeGreaterThanOrEqual(180);
    const closedMinWidth = trigger.element.style.minWidth;
    const triggerWidth = Number.parseFloat(closedMinWidth);
    vi.spyOn(trigger.element as HTMLButtonElement, "getBoundingClientRect").mockReturnValue({
      x: 0,
      y: 0,
      top: 0,
      left: 0,
      right: triggerWidth,
      bottom: 40,
      width: triggerWidth,
      height: 40,
      toJSON: () => ({}),
    });

    await trigger.trigger("click");
    await nextTick();
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

    const dialog = document.querySelector(
      '[role="dialog"][aria-label="filters"]',
    ) as HTMLElement | null;
    expect(dialog).toBeTruthy();
    // Trigger keeps a stable size when the panel opens.
    expect(trigger.element.style.minWidth).toBe(closedMinWidth);
    // Panel locks to the same width as the filter bar.
    expect(dialog!.style.width).toBe(`${triggerWidth}px`);
    expect(dialog!.style.minWidth).toBe(`${triggerWidth}px`);
    expect(dialog!.style.maxWidth).toBe(`${triggerWidth}px`);

    const chip = dialog!.querySelector("button[aria-pressed]") as HTMLButtonElement | null;
    const clear = Array.from(dialog!.querySelectorAll("button")).find(
      (btn) => btn.textContent?.trim() === "clear",
    ) as HTMLButtonElement | undefined;
    expect(chip).toBeTruthy();
    expect(clear).toBeTruthy();
    // Same chip geometry (not tall BaseButton h-10).
    expect(clear!.className).toContain("h-9");
    expect(chip!.className).toContain("h-9");

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
    // Locked to the filter bar — same width, min, and max.
    expect(dialog!.style.width).toBe("288px");
    expect(dialog!.style.minWidth).toBe("288px");
    expect(dialog!.style.maxWidth).toBe("288px");

    wrapper.unmount();
  });

  it("keeps a local-anchor panel under the root with shared min-width", async () => {
    const wrapper = mount(AdminFilterDropdown, {
      props: {
        anchor: "local",
        label: "options",
        showFilterIcon: false,
        showClear: false,
        optionLabels: ["auto", "custom delimiters"],
        activeLabel: "auto",
      },
      slots: {
        default: `
          <label>
            format
            <select aria-label="format">
              <option>auto</option>
              <option>custom delimiters</option>
            </select>
          </label>
        `,
      },
      attachTo: document.body,
    });

    await nextTick();

    // jsdom often reports 0 scrollWidth — seed the probe like BaseDropdownMenu tests seed rects.
    const measure = wrapper.element.querySelector(
      '[aria-hidden="true"].pointer-events-none',
    ) as HTMLElement | null;
    expect(measure).toBeTruthy();
    Object.defineProperty(measure!, "scrollWidth", { configurable: true, get: () => 240 });
    for (const node of measure!.querySelectorAll<HTMLElement>(
      "button, input, select, textarea, label, span",
    )) {
      Object.defineProperty(node, "scrollWidth", { configurable: true, get: () => 220 });
    }
    window.dispatchEvent(new Event("resize"));
    await nextTick();
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

    const root = wrapper.element as HTMLElement;
    expect(Number.parseFloat(root.style.minWidth)).toBeGreaterThanOrEqual(220);

    const trigger = wrapper.get('button[aria-haspopup="dialog"]');
    await trigger.trigger("click");
    await nextTick();

    const dialog = wrapper.find('[role="dialog"][aria-label="options"]');
    expect(dialog.exists()).toBe(true);
    // Local: stays in the component tree (not a body teleport child).
    expect(root.contains(dialog.element)).toBe(true);
    expect(dialog.element.parentElement).not.toBe(document.body);
    // Absolute under trigger — no fixed JS coordinates.
    expect(dialog.classes()).toContain("absolute");
    expect(dialog.classes()).toContain("left-0");
    expect(dialog.classes()).toContain("right-0");
    expect(dialog.element.style.top).toBe("");
    expect(dialog.element.style.left).toBe("");
    expect(dialog.element.style.width).toBe("");

    wrapper.unmount();
  });
});
