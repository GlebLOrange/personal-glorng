import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { describe, expect, it, vi } from "vitest";

import BaseDropdownMenu from "@/components/ui/BaseDropdownMenu.vue";
import BaseDropdownMenuItem from "@/components/ui/BaseDropdownMenuItem.vue";

describe("BaseDropdownMenu", () => {
  it("names the icon trigger and moves focus into the menu", async () => {
    const wrapper = mount(BaseDropdownMenu, {
      props: { ariaLabel: "recipe actions" },
      slots: {
        default: `
          <button type="button" role="menuitem">edit</button>
          <button type="button" role="menuitem">delete</button>
        `,
      },
      attachTo: document.body,
    });

    const trigger = wrapper.get('button[aria-label="recipe actions"]');
    expect(trigger.attributes("aria-haspopup")).toBe("menu");
    expect(trigger.attributes("aria-expanded")).toBe("false");

    await trigger.trigger("click");
    await nextTick();

    expect(trigger.attributes("aria-expanded")).toBe("true");
    expect(document.activeElement?.getAttribute("role")).toBe("menuitem");
    expect(document.activeElement?.textContent).toContain("edit");

    wrapper.unmount();
  });

  it("supports arrow-key movement between menu items", async () => {
    const wrapper = mount(BaseDropdownMenu, {
      slots: {
        default: `
          <button type="button" role="menuitem">one</button>
          <button type="button" role="menuitem">two</button>
        `,
      },
      attachTo: document.body,
    });

    await wrapper.get("button").trigger("click");
    await nextTick();

    document.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowDown" }));
    await nextTick();
    expect(document.activeElement?.textContent).toContain("two");

    wrapper.unmount();
  });

  it("keeps the trigger labeled even with a custom trigger slot", () => {
    const wrapper = mount(BaseDropdownMenu, {
      props: { ariaLabel: "more actions" },
      slots: {
        trigger: "more",
        default: '<button type="button" role="menuitem">edit</button>',
      },
    });

    expect(wrapper.get('button[aria-label="more actions"]').text()).toContain("more");
  });

  it("paints icon-only triggers with the requested family", () => {
    const wrapper = mount(BaseDropdownMenu, {
      props: { ariaLabel: "edit", iconOnly: true, family: "3xx" },
      slots: {
        trigger: "<span>✎</span>",
        default: '<button type="button" role="menuitem">reopen</button>',
      },
    });

    const trigger = wrapper.get('button[aria-label="edit"]');
    expect(trigger.classes()).toContain("text-status-warning");
    expect(trigger.classes()).toContain("bg-status-warning/3");
  });

  it("sizes a labeled trigger to the longest menu item to avoid jumping", async () => {
    const wrapper = mount(BaseDropdownMenu, {
      props: { ariaLabel: "more actions" },
      slots: {
        trigger: "<span>more actions</span>",
        default: `
          <button type="button" role="menuitem">reopen</button>
          <button type="button" role="menuitem">didn't finish</button>
          <button type="button" role="menuitem">cancel task</button>
        `,
      },
      attachTo: document.body,
    });

    const trigger = wrapper.get('button[aria-label="more actions"]').element as HTMLButtonElement;
    vi.spyOn(trigger, "getBoundingClientRect").mockReturnValue({
      x: 0,
      y: 0,
      top: 0,
      left: 0,
      right: 140,
      bottom: 40,
      width: 140,
      height: 40,
      toJSON: () => ({}),
    });
    for (const item of wrapper.element.querySelectorAll<HTMLElement>('[role="menuitem"]')) {
      const width = (item.textContent?.trim().length ?? 0) * 8;
      vi.spyOn(item, "getBoundingClientRect").mockReturnValue({
        x: 0,
        y: 0,
        top: 0,
        left: 0,
        right: width,
        bottom: 32,
        width,
        height: 32,
        toJSON: () => ({}),
      });
    }

    await nextTick();
    // Remount-measure: open once so sync runs with spies in place.
    await wrapper.get('button[aria-label="more actions"]').trigger("click");
    await nextTick();

    const root = wrapper.element as HTMLElement;
    // "didn't finish" ~13*8 + chrome 16 = 120; trigger 140 → keep 140+
    expect(Number.parseFloat(root.style.minWidth)).toBeGreaterThanOrEqual(140);

    wrapper.unmount();
  });

  it("closes when focus leaves the menu", async () => {
    const wrapper = mount(BaseDropdownMenu, {
      slots: {
        default: `
          <button type="button" role="menuitem">one</button>
          <button type="button" role="menuitem">two</button>
        `,
      },
      attachTo: document.body,
    });

    const trigger = wrapper.get("button");
    await trigger.trigger("click");
    await nextTick();

    const outside = document.createElement("button");
    outside.type = "button";
    document.body.append(outside);
    document.activeElement?.dispatchEvent(
      new FocusEvent("focusout", {
        bubbles: true,
        relatedTarget: outside,
      }),
    );
    outside.focus();
    await nextTick();

    expect(trigger.attributes("aria-expanded")).toBe("false");

    outside.remove();
    wrapper.unmount();
  });
});

describe("BaseDropdownMenuItem", () => {
  it("exposes menuitem role", () => {
    const wrapper = mount(BaseDropdownMenuItem, {
      slots: { default: "edit" },
    });
    expect(wrapper.get("button").attributes("role")).toBe("menuitem");
  });
});
