import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import { Card, CardTitle } from "@/components/ui/card";

describe("Card", () => {
  it("renders default panel variant", () => {
    const wrapper = mount(Card, {
      slots: { default: "content" },
    });

    expect(wrapper.classes()).toEqual(
      expect.arrayContaining(["rounded-lg", "p-6", "bg-surface-card", "border-surface-border"]),
    );
    expect(wrapper.text()).toBe("content");
  });

  it("renders compact variant", () => {
    const wrapper = mount(Card, {
      props: { variant: "compact" },
    });

    expect(wrapper.classes()).toEqual(expect.arrayContaining(["p-4"]));
  });

  it("renders danger tint", () => {
    const wrapper = mount(Card, {
      props: { tint: "danger" },
    });

    expect(wrapper.classes()).toEqual(
      expect.arrayContaining(["border-status-error/60", "bg-status-error/10"]),
    );
  });

  it("renders hoverable interactive button", () => {
    const wrapper = mount(Card, {
      props: {
        as: "button",
        hoverable: true,
        interactive: true,
        variant: "compact",
      },
      attrs: { type: "button" },
    });

    expect(wrapper.element.tagName).toBe("BUTTON");
    expect(wrapper.classes()).toEqual(
      expect.arrayContaining(["hover:border-accent-blue", "focus-visible:ring-accent-blue/50"]),
    );
  });

  it("adds keyboard semantics for interactive non-button cards", async () => {
    const onClick = vi.fn();
    const wrapper = mount(Card, {
      props: { interactive: true, variant: "compact" },
      attrs: { onClick },
    });

    expect(wrapper.attributes("role")).toBe("button");
    expect(wrapper.attributes("tabindex")).toBe("0");

    await wrapper.trigger("keydown", { key: "Enter" });
    expect(onClick).toHaveBeenCalledTimes(1);

    await wrapper.trigger("keydown", { key: " " });
    expect(onClick).toHaveBeenCalledTimes(2);
  });
});

describe("CardTitle", () => {
  it("uses card-title utility", () => {
    const wrapper = mount(CardTitle, {
      slots: { default: "Profile" },
    });

    expect(wrapper.classes()).toContain("card-title");
    expect(wrapper.text()).toBe("Profile");
  });
});
