import { defineComponent, nextTick } from "vue";
import { mount } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useLiveLocalTime } from "@/composables/useLiveLocalTime";

const ClockHarness = defineComponent({
  props: {
    offsetHours: { type: Number, default: null },
    ianaTimezone: { type: String, default: null },
  },
  setup(props) {
    const { liveTime } = useLiveLocalTime(
      () => props.offsetHours,
      "time-seconds",
      () => props.ianaTimezone,
    );
    return { liveTime };
  },
  template: "<span>{{ liveTime }}</span>",
});

describe("useLiveLocalTime", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    Object.defineProperty(document, "hidden", {
      configurable: true,
      get: () => false,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("ticks seconds via IANA timezone", async () => {
    vi.setSystemTime(new Date("2026-07-14T01:35:00Z"));

    const wrapper = mount(ClockHarness, {
      props: { offsetHours: 2, ianaTimezone: "Europe/Warsaw" },
    });
    await nextTick();
    expect(wrapper.text()).toBe("03:35:00");

    vi.advanceTimersByTime(5_000);
    await nextTick();
    expect(wrapper.text()).toBe("03:35:05");
    wrapper.unmount();
  });

  it("falls back to offset-only clock without IANA timezone", async () => {
    vi.setSystemTime(new Date("2025-06-07T12:00:00Z"));
    vi.spyOn(Date.prototype, "getTimezoneOffset").mockReturnValue(0);

    const wrapper = mount(ClockHarness, {
      props: { offsetHours: 3, ianaTimezone: null },
    });
    await nextTick();
    expect(wrapper.text()).toBe("15:00:00");
    wrapper.unmount();
  });

  it("falls back to offset clock when IANA timezone is invalid", async () => {
    vi.setSystemTime(new Date("2025-06-07T12:00:00Z"));
    vi.spyOn(Date.prototype, "getTimezoneOffset").mockReturnValue(0);

    const wrapper = mount(ClockHarness, {
      props: { offsetHours: 3, ianaTimezone: "Foo/Bar" },
    });
    await nextTick();
    expect(wrapper.text()).toBe("15:00:00");
    wrapper.unmount();
  });

  it("shares one interval across multiple mounts", async () => {
    const setIntervalSpy = vi.spyOn(globalThis, "setInterval");
    vi.setSystemTime(new Date("2026-07-14T01:35:00Z"));

    const first = mount(ClockHarness, {
      props: { offsetHours: 2, ianaTimezone: "Europe/Warsaw" },
    });
    const second = mount(ClockHarness, {
      props: { offsetHours: 2, ianaTimezone: "Europe/Warsaw" },
    });
    await nextTick();

    expect(setIntervalSpy).toHaveBeenCalledTimes(1);

    vi.advanceTimersByTime(2_000);
    await nextTick();
    expect(first.text()).toBe("03:35:02");
    expect(second.text()).toBe("03:35:02");

    first.unmount();
    second.unmount();
  });

  it("pauses ticking while the document is hidden", async () => {
    let hidden = false;
    Object.defineProperty(document, "hidden", {
      configurable: true,
      get: () => hidden,
    });

    vi.setSystemTime(new Date("2026-07-14T01:35:00Z"));
    const wrapper = mount(ClockHarness, {
      props: { offsetHours: 2, ianaTimezone: "Europe/Warsaw" },
    });
    await nextTick();
    expect(wrapper.text()).toBe("03:35:00");

    hidden = true;
    document.dispatchEvent(new Event("visibilitychange"));
    vi.advanceTimersByTime(5_000);
    await nextTick();
    expect(wrapper.text()).toBe("03:35:00");

    hidden = false;
    vi.setSystemTime(new Date("2026-07-14T01:35:10Z"));
    document.dispatchEvent(new Event("visibilitychange"));
    await nextTick();
    expect(wrapper.text()).toBe("03:35:10");

    wrapper.unmount();
  });
});
