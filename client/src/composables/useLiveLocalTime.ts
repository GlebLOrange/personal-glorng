import { onMounted, onUnmounted, ref, watch, type MaybeRefOrGetter, type Ref, toValue } from "vue";

import {
  formatLiveLocalDateTime,
  formatLiveLocalTime,
  formatLiveLocalTimeWithSeconds,
  isoDateTimeFromOffset,
} from "@/utils/weather";

type LiveTimeFormat = "time" | "time-seconds" | "datetime";

/** Tick every second with local time for a UTC offset in hours. */
export function useLiveLocalTime(
  offsetHours: MaybeRefOrGetter<number | null>,
  format: MaybeRefOrGetter<LiveTimeFormat> = "datetime",
): { liveTime: Ref<string | null>; liveDateTime: Ref<string | null> } {
  const liveTime = ref<string | null>(null);
  const liveDateTime = ref<string | null>(null);
  let timer: ReturnType<typeof setInterval> | null = null;

  function update(): void {
    const offset = toValue(offsetHours);
    if (offset === null) {
      liveTime.value = null;
      liveDateTime.value = null;
      return;
    }
    const fmt = toValue(format);
    liveTime.value =
      fmt === "datetime"
        ? formatLiveLocalDateTime(offset)
        : fmt === "time-seconds"
          ? formatLiveLocalTimeWithSeconds(offset)
          : formatLiveLocalTime(offset);
    liveDateTime.value = isoDateTimeFromOffset(offset);
  }

  onMounted(() => {
    update();
    timer = setInterval(update, 1_000);
  });

  onUnmounted(() => {
    if (timer) {
      clearInterval(timer);
    }
  });

  watch(() => [toValue(offsetHours), toValue(format)] as const, update);

  return { liveTime, liveDateTime };
}
