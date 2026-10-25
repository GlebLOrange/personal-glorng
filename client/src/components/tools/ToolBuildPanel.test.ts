import { mount, flushPromises } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ToolBuildPanel from "@/components/tools/ToolBuildPanel.vue";

describe("ToolBuildPanel", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders how-this-is-built copy for a known slug", () => {
    const wrapper = mount(ToolBuildPanel, { props: { slug: "weather" } });
    expect(wrapper.text()).toContain("how this is built");
    expect(wrapper.text()).toContain("/weather");
    expect(wrapper.get("details").attributes("open")).toBeDefined();
  });

  it("collapses the spoiler after five seconds", async () => {
    const wrapper = mount(ToolBuildPanel, { props: { slug: "qr-generator" } });
    expect(wrapper.get("details").attributes("open")).toBeDefined();

    vi.advanceTimersByTime(5000);
    await flushPromises();

    expect(wrapper.get("details").attributes("open")).toBeUndefined();
  });

  it("cancels auto-collapse when the user toggles the panel", async () => {
    const wrapper = mount(ToolBuildPanel, { props: { slug: "qr-generator" } });
    // jsdom leaves details.open true; toggle only clears the timer.
    await wrapper.get("details").trigger("toggle");

    vi.advanceTimersByTime(5000);
    await flushPromises();

    expect(wrapper.get("details").attributes("open")).toBeDefined();
  });

  it("renders nothing for an unknown slug", () => {
    const wrapper = mount(ToolBuildPanel, { props: { slug: "tasks" } });
    expect(wrapper.find("details").exists()).toBe(false);
  });
});
