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
  });

  it("falls back to offset-only clock without IANA timezone", async () => {
    vi.setSystemTime(new Date("2025-06-07T12:00:00Z"));
    vi.spyOn(Date.prototype, "getTimezoneOffset").mockReturnValue(0);

    const wrapper = mount(ClockHarness, {
      props: { offsetHours: 3, ianaTimezone: null },
    });
    await nextTick();
    expect(wrapper.text()).toBe("15:00:00");
  });

  it("falls back to offset clock when IANA timezone is invalid", async () => {
    vi.setSystemTime(new Date("2025-06-07T12:00:00Z"));
    vi.spyOn(Date.prototype, "getTimezoneOffset").mockReturnValue(0);

    const wrapper = mount(ClockHarness, {
      props: { offsetHours: 3, ianaTimezone: "Foo/Bar" },
    });
    await nextTick();
    expect(wrapper.text()).toBe("15:00:00");
  });
});
