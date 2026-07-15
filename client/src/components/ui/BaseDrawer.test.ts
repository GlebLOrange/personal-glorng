import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, describe, expect, it } from "vitest";
import { nextTick } from "vue";

import BaseDrawer from "@/components/ui/BaseDrawer.vue";

function mountDrawer(open = true): { wrapper: VueWrapper; trigger: HTMLButtonElement } {
  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.textContent = "Open drawer";
  document.body.append(trigger);
  trigger.focus();

  const wrapper = mount(BaseDrawer, {
    attachTo: document.body,
    props: { open, title: "Drawer title" },
    slots: { default: "<p>Drawer body</p>" },
  });

  return { wrapper, trigger };
}

afterEach(() => {
  document.body.innerHTML = "";
});

describe("BaseDrawer", () => {
  it("hides backdrop from assistive tech and exposes dialog semantics", async () => {
    const { wrapper } = mountDrawer();
    await nextTick();

    expect(document.body.querySelector('[aria-hidden="true"]')).not.toBeNull();
    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog?.getAttribute("aria-modal")).toBe("true");
    expect(dialog?.getAttribute("aria-label")).toBe("Drawer title");

    wrapper.unmount();
  });

  it("closes on Escape and restores focus when closed", async () => {
    const { wrapper, trigger } = mountDrawer();
    await nextTick();

    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    expect(wrapper.emitted("close")).toHaveLength(1);

    await wrapper.setProps({ open: false });
    await nextTick();
    expect(document.activeElement).toBe(trigger);

    wrapper.unmount();
  });

  it("does not render when closed", () => {
    const { wrapper } = mountDrawer(false);

    expect(document.body.querySelector('[role="dialog"]')).toBeNull();

    wrapper.unmount();
  });
});
