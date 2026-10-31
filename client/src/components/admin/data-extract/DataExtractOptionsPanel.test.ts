import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { describe, expect, it } from "vitest";

import DataExtractOptionsPanel from "@/components/admin/data-extract/DataExtractOptionsPanel.vue";

describe("DataExtractOptionsPanel popover a11y", () => {
  it("focuses the first control on open, closes on Escape, and restores trigger focus", async () => {
    const wrapper = mount(DataExtractOptionsPanel, {
      props: {
        formatChoice: "auto",
        profileChoice: "custom",
        fieldDelimiter: "|",
        listDelimiter: ";",
        rowTag: "",
        xmlMode: "rows",
        hasCustomOptions: false,
        showDelimitedOptions: false,
        showXmlOptions: true,
      },
      attachTo: document.body,
    });

    const trigger = wrapper.get('button[aria-haspopup="dialog"]');
    (trigger.element as HTMLButtonElement).focus();
    await trigger.trigger("click");
    await nextTick();

    // Portal: panel teleports to body so the options trigger can stay compact in the toolbar.
    const dialog = document.querySelector('[role="dialog"][aria-label="options"]');
    expect(dialog).toBeTruthy();
    expect(wrapper.element.contains(dialog!)).toBe(false);
    expect(dialog!.parentElement).toBe(document.body);
    expect(dialog!.classList.contains("fixed")).toBe(true);
    expect(dialog!.contains(document.activeElement)).toBe(true);
    expect(document.activeElement?.tagName).toBe("SELECT");

    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    await nextTick();
    expect(document.querySelector('[role="dialog"][aria-label="options"]')).toBeNull();
    expect(document.activeElement).toBe(trigger.element);

    wrapper.unmount();
  });
});
