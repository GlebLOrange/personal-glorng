import { defineComponent, nextTick } from "vue";
import { mount } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useLiveLocalTime } from "@/composables/useLiveLocalTime";

const ANCHOR_UNIXTIME = 1_780_833_600;
const OFFSET_HOURS = 2;

const ClockHarness = defineComponent({
  props: {
    offsetHours: { type: Number, required: true },
    anchorUnixtime: { type: Number, default: null },
  },
  setup(props) {
    const { liveTime } = useLiveLocalTime(
      () => props.offsetHours,
      "time-seconds",
      () => props.anchorUnixtime,
    );
    return { liveTime };
  },
  template: "<span>{{ liveTime }}</span>",
});

describe("useLiveLocalTime", () => {
  let perfNow = 1_000;

  beforeEach(() => {
    vi.useFakeTimers();
    perfNow = 1_000;
    vi.spyOn(performance, "now").mockImplementation(() => perfNow);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("advances seconds from anchored unixtime", async () => {
    const wrapper = mount(ClockHarness, {
      props: { offsetHours: OFFSET_HOURS, anchorUnixtime: ANCHOR_UNIXTIME },
    });
    await nextTick();
    expect(wrapper.text()).toBe("14:00:00");

    perfNow += 5_000;
    vi.advanceTimersByTime(5_000);
    await nextTick();
    expect(wrapper.text()).toBe("14:00:05");
  });

  it("falls back to offset-only clock without anchor", async () => {
    vi.setSystemTime(new Date("2025-06-07T12:00:00Z"));
    vi.spyOn(Date.prototype, "getTimezoneOffset").mockReturnValue(0);

    const wrapper = mount(ClockHarness, {
      props: { offsetHours: 3, anchorUnixtime: null },
    });
    await nextTick();
    expect(wrapper.text()).toBe("15:00:00");
  });
});
