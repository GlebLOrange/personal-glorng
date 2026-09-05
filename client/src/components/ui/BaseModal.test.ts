import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, describe, expect, it } from "vitest";
import { nextTick } from "vue";

import BaseModal from "@/components/ui/BaseModal.vue";

async function flushFocus(): Promise<void> {
  await nextTick();
  await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
}

function mountModal(
  props: {
    open?: boolean;
    title?: string;
    ariaLabel?: string;
  } = { open: true, title: "Test modal" },
): { wrapper: VueWrapper; trigger: HTMLButtonElement } {
  const trigger = document.createElement("button");
  trigger.type = "button";
  trigger.textContent = "Open";
  document.body.append(trigger);
  trigger.focus();

  const wrapper = mount(BaseModal, {
    attachTo: document.body,
    props: { open: true, ...props },
    slots: {
      default: '<input type="text" aria-label="sample field" />',
    },
  });

  return { wrapper, trigger };
}

afterEach(() => {
  document.body.innerHTML = "";
});

describe("BaseModal", () => {
  it("exposes dialog semantics", async () => {
    const { wrapper } = mountModal();
    await flushFocus();

    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog).not.toBeNull();
    expect(dialog?.getAttribute("aria-modal")).toBe("true");
    expect(dialog?.getAttribute("aria-labelledby")).toBeTruthy();
    expect(document.body.querySelector(".overlay-backdrop")).not.toBeNull();

    wrapper.unmount();
  });

  it("does not render when closed", () => {
    const { wrapper } = mountModal({ open: false, title: "Hidden" });

    expect(document.body.querySelector('[role="dialog"]')).toBeNull();

    wrapper.unmount();
  });

  it("focuses the first editable field on open, not the close button", async () => {
    const { wrapper } = mountModal();
    await flushFocus();

    const field = document.body.querySelector(
      'input[aria-label="sample field"]',
    ) as HTMLInputElement | null;
    expect(document.activeElement).toBe(field);

    wrapper.unmount();
  });

  it("closes on Escape and restores focus", async () => {
    const { wrapper, trigger } = mountModal();
    await flushFocus();

    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    expect(wrapper.emitted("close")).toHaveLength(1);

    await wrapper.setProps({ open: false });
    await nextTick();
    expect(document.activeElement).toBe(trigger);

    wrapper.unmount();
  });

  it("traps Tab focus inside the dialog", async () => {
    const { wrapper } = mountModal();
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

  it("uses ariaLabel when no title is provided", async () => {
    const { wrapper } = mountModal({ open: true, ariaLabel: "confirm delete" });
    await flushFocus();

    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog?.getAttribute("aria-label")).toBe("confirm delete");
    expect(dialog?.getAttribute("aria-labelledby")).toBeNull();

    wrapper.unmount();
  });

  it("keeps aria-labelledby valid when a custom header slot omits the title id", async () => {
    const trigger = document.createElement("button");
    trigger.type = "button";
    document.body.append(trigger);
    trigger.focus();

    const wrapper = mount(BaseModal, {
      attachTo: document.body,
      props: { open: true, title: "Custom title fallback" },
      slots: {
        header: "<div>Custom header</div>",
        default: '<input type="text" aria-label="sample field" />',
      },
    });
    await flushFocus();

    const dialog = document.body.querySelector('[role="dialog"]');
    const labelledBy = dialog?.getAttribute("aria-labelledby");
    expect(labelledBy).toBeTruthy();
    expect(document.getElementById(labelledBy! as string)?.textContent).toBe(
      "Custom title fallback",
    );

    wrapper.unmount();
  });

  it("falls back to Dialog aria-label when no title or ariaLabel", async () => {
    const { wrapper } = mountModal({ open: true });
    await flushFocus();

    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog?.getAttribute("aria-label")).toBe("dialog");
    expect(dialog?.getAttribute("aria-labelledby")).toBeNull();

    wrapper.unmount();
  });
});
