import { onMounted, onUnmounted, ref, watch, type MaybeRefOrGetter, type Ref, toValue } from "vue";

import { formatLiveLocalDateTime, formatLiveLocalTime } from "@/utils/weather";

type LiveTimeFormat = "time" | "datetime";

/** Tick every second with local time for a UTC offset in hours. */
export function useLiveLocalTime(
  offsetHours: MaybeRefOrGetter<number | null>,
  format: LiveTimeFormat = "datetime",
): { liveTime: Ref<string | null> } {
  const liveTime = ref<string | null>(null);
  let timer: ReturnType<typeof setInterval> | null = null;

  function update(): void {
    const offset = toValue(offsetHours);
    if (offset === null) {
      liveTime.value = null;
      return;
    }
    liveTime.value =
      format === "datetime" ? formatLiveLocalDateTime(offset) : formatLiveLocalTime(offset);
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

  watch(() => toValue(offsetHours), update);

  return { liveTime };
}
