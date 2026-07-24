import { afterEach, describe, expect, it } from "vitest";
import { effectScope, nextTick, ref } from "vue";

import { getOverlayFocusableElements, useOverlayShell } from "@/composables/useOverlayShell";

afterEach(() => {
  document.body.innerHTML = "";
  document.body.style.overflow = "";
});

describe("getOverlayFocusableElements", () => {
  it("returns tabbable controls and skips negative tabindex", () => {
    const root = document.createElement("div");
    root.innerHTML = `
      <button type="button">One</button>
      <button type="button" tabindex="-1">Skip</button>
      <input type="text" />
      <a href="/x">Link</a>
    `;

    const focusables = getOverlayFocusableElements(root);
    expect(focusables).toHaveLength(3);
    expect(focusables.map((el) => el.tagName)).toEqual(["BUTTON", "INPUT", "A"]);
  });
});

describe("useOverlayShell", () => {
  it("emits close on Escape while open", async () => {
    const open = ref(true);
    const panel = ref<HTMLElement | null>(document.createElement("div"));
    panel.value!.innerHTML = '<button type="button">Close</button>';
    document.body.append(panel.value!);

    let closed = 0;
    const scope = effectScope();
    scope.run(() => {
      useOverlayShell({
        open,
        panelRef: panel,
        onClose: () => {
          closed += 1;
        },
      });
    });
    await nextTick();

    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    expect(closed).toBe(1);

    open.value = false;
    await nextTick();
    scope.stop();
  });
});
