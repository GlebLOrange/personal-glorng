import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import FieldHelp from "@/components/ui/FieldHelp.vue";

describe("FieldHelp", () => {
  it("teleports a top-end tip with an arrow when opened", async () => {
    const wrapper = mount(FieldHelp, {
      props: {
        text: "smart text tip",
        placement: "top",
        align: "end",
        size: "sm",
        contentId: "field-help-test-hint",
      },
      attachTo: document.body,
    });

    const button = wrapper.get('button[aria-label="help"]');
    await button.trigger("click");

    const tip = document.body.querySelector('[role="tooltip"]');
    expect(tip).not.toBeNull();
    expect(tip?.textContent).toContain("smart text tip");
    expect(tip?.querySelector('[aria-hidden="true"]')).not.toBeNull();
    expect(button.attributes("aria-expanded")).toBe("true");
    expect(button.attributes("aria-controls")).toBe("field-help-test-hint");

    wrapper.unmount();
  });
});
