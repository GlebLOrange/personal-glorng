import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import ToolIcon from "@/components/icons/ToolIcon.vue";
import { PLATFORM_SERVICES } from "@/platform/services";

const KNOWN_SLUGS = [
  ...PLATFORM_SERVICES.map((s) => s.slug),
  "users",
  "sync",
  "location",
  "unknown-fallback",
] as const;

describe("ToolIcon", () => {
  it.each(KNOWN_SLUGS)("renders an svg for slug %s", (slug) => {
    const wrapper = mount(ToolIcon, { props: { slug } });
    expect(wrapper.find("svg").exists()).toBe(true);
    expect(wrapper.find("svg").attributes("aria-hidden")).toBe("true");
  });
});
