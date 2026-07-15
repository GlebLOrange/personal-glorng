import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, describe, expect, it } from "vitest";
import { nextTick } from "vue";

import BaseModal from "@/components/ui/BaseModal.vue";

function mountModal(title = "Test modal"): { wrapper: VueWrapper; trigger: HTMLButtonElement } {
  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.textContent = "Open";
  document.body.append(trigger);
  trigger.focus();

  const wrapper = mount(BaseModal, {
    attachTo: document.body,
    props: { title },
    slots: {
      default: '<input type="text" aria-label="Sample field" />',
    },
  });

  return { wrapper, trigger };
}

afterEach(() => {
  document.body.innerHTML = "";
});

describe("BaseModal", () => {
  it("exposes dialog semantics", () => {
    const { wrapper } = mountModal();

    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog).not.toBeNull();
    expect(dialog?.getAttribute("aria-modal")).toBe("true");
    expect(dialog?.getAttribute("aria-labelledby")).toBe("modal-title");

    wrapper.unmount();
  });

  it("closes on Escape and restores focus", async () => {
    const { wrapper, trigger } = mountModal();
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    expect(wrapper.emitted("close")).toHaveLength(1);

    wrapper.unmount();
    await nextTick();
    expect(document.activeElement).toBe(trigger);
  });

  it("traps Tab focus inside the dialog", async () => {
    const { wrapper } = mountModal();
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

    const dialog = document.body.querySelector('[role="dialog"]') as HTMLElement;
    const focusables = dialog.querySelectorAll<HTMLElement>(
      'button:not([disabled]), input:not([disabled])',
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
