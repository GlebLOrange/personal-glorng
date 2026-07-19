import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { describe, expect, it } from "vitest";

import BaseDropdownMenu from "@/components/ui/BaseDropdownMenu.vue";
import BaseDropdownMenuItem from "@/components/ui/BaseDropdownMenuItem.vue";

describe("BaseDropdownMenu", () => {
  it("names the icon trigger and moves focus into the menu", async () => {
    const wrapper = mount(BaseDropdownMenu, {
      props: { ariaLabel: "Recipe actions" },
      slots: {
        default: `
          <button type="button" role="menuitem">edit</button>
          <button type="button" role="menuitem">delete</button>
        `,
      },
      attachTo: document.body,
    });

    const trigger = wrapper.get('button[aria-label="Recipe actions"]');
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
});

describe("BaseDropdownMenuItem", () => {
  it("exposes menuitem role", () => {
    const wrapper = mount(BaseDropdownMenuItem, {
      slots: { default: "edit" },
    });
    expect(wrapper.get("button").attributes("role")).toBe("menuitem");
  });
});
