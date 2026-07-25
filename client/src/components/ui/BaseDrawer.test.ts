import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, describe, expect, it } from "vitest";
import { nextTick } from "vue";

import BaseDrawer from "@/components/ui/BaseDrawer.vue";

async function flushFocus(): Promise<void> {
  await nextTick();
  await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
}

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
    await flushFocus();

    const backdrop = document.body.querySelector(".overlay-backdrop");
    expect(backdrop?.getAttribute("aria-hidden")).toBe("true");
    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog?.getAttribute("aria-modal")).toBe("true");
    expect(dialog?.getAttribute("aria-labelledby")).toBeTruthy();
    expect(dialog?.hasAttribute("aria-label")).toBe(false);

    wrapper.unmount();
  });

  it("wires aria-labelledby through a custom #title slot", async () => {
    const trigger = document.createElement("button");
    trigger.type = "button";
    document.body.append(trigger);
    trigger.focus();

    const wrapper = mount(BaseDrawer, {
      attachTo: document.body,
      props: { open: true, title: "Fallback title" },
      slots: {
        // Scoped slot props are in scope for string slot templates.
        title: '<h2 :id="titleId">Custom title</h2>',
        default: "<p>Drawer body</p>",
      },
    });
    await flushFocus();

    const dialog = document.body.querySelector('[role="dialog"]');
    const labelledBy = dialog?.getAttribute("aria-labelledby");
    expect(labelledBy).toBeTruthy();
    const title = document.getElementById(labelledBy!);
    expect(title?.textContent).toBe("Custom title");

    wrapper.unmount();
  });

  it("focuses the first editable field when the drawer opens", async () => {
    const trigger = document.createElement("button");
    trigger.type = "button";
    document.body.append(trigger);
    trigger.focus();

    const wrapper = mount(BaseDrawer, {
      attachTo: document.body,
      props: { open: true, title: "Edit item" },
      slots: {
        default: '<input type="text" aria-label="Title field" />',
      },
    });
    await flushFocus();

    const field = document.body.querySelector(
      'input[aria-label="Title field"]',
    ) as HTMLInputElement | null;
    expect(document.activeElement).toBe(field);

    wrapper.unmount();
  });

  it("falls back to the close button when there is no editable field", async () => {
    const { wrapper } = mountDrawer();
    await flushFocus();

    const close = document.body.querySelector(
      'button[aria-label="Close drawer"]',
    ) as HTMLButtonElement | null;
    expect(close).not.toBeNull();
    expect(document.activeElement).toBe(close);

    wrapper.unmount();
  });

  it("closes on Escape and restores focus when closed", async () => {
    const { wrapper, trigger } = mountDrawer();
    await flushFocus();

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

  it("traps Tab focus inside the drawer", async () => {
    const trigger = document.createElement("button");
    trigger.type = "button";
    document.body.append(trigger);
    trigger.focus();

    const wrapper = mount(BaseDrawer, {
      attachTo: document.body,
      props: { open: true, title: "Trap" },
      slots: {
        default: '<input type="text" aria-label="Field" />',
      },
    });
    await flushFocus();

    const dialog = document.body.querySelector('[role="dialog"]') as HTMLElement;
    const focusables = dialog.querySelectorAll<HTMLElement>(
      "button:not([disabled]), input:not([disabled])",
    );
    const last = focusables[focusables.length - 1];
    last.focus();

    document.dispatchEvent(
      new KeyboardEvent("keydown", { key: "Tab", bubbles: true, cancelable: true }),
    );
    expect(document.activeElement).toBe(focusables[0]);

    wrapper.unmount();
  });
});
