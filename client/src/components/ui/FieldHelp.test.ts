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

  it("keeps sm glyph small while exposing a ≥44×44 hit box", () => {
    const wrapper = mount(FieldHelp, {
      props: {
        text: "page description",
        size: "sm",
      },
      attachTo: document.body,
    });

    const button = wrapper.get('button[aria-label="help"]');
    expect(button.classes()).toEqual(
      expect.arrayContaining(["min-h-11", "min-w-11"]),
    );
    expect(button.find("svg").classes()).toEqual(expect.arrayContaining(["size-3"]));

    wrapper.unmount();
  });

  it("opens on keyboard focus when interactive (default)", async () => {
    const wrapper = mount(FieldHelp, {
      props: {
        text: "keyboard reachable tip",
        size: "sm",
      },
      attachTo: document.body,
    });

    const button = wrapper.get('button[aria-label="help"]');
    await button.trigger("focus");

    expect(button.attributes("aria-expanded")).toBe("true");
    expect(document.body.querySelector('[role="tooltip"]')).not.toBeNull();

    wrapper.unmount();
  });
});
