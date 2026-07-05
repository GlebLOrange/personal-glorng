import { onMounted, onUnmounted, ref, watch, type MaybeRefOrGetter, type Ref, toValue } from "vue";

import {
  formatLiveLocalDate,
  formatLiveLocalDateFromUnix,
  formatLiveLocalDateTime,
  formatLiveLocalDateTimeFromUnix,
  formatLiveLocalTime,
  formatLiveLocalTimeFromUnix,
  formatLiveLocalTimeWithSeconds,
  formatLiveLocalTimeWithSecondsFromUnix,
  isoDateFromOffset,
  isoDateFromUnix,
  isoDateTimeFromOffset,
  isoDateTimeFromUnix,
} from "@/utils/weather";

type LiveTimeFormat = "time" | "time-seconds" | "datetime" | "date";

/** Tick every second with local time synced to World Time API or UTC offset. */
export function useLiveLocalTime(
  offsetHours: MaybeRefOrGetter<number | null>,
  format: MaybeRefOrGetter<LiveTimeFormat> = "datetime",
  anchorUnixtime?: MaybeRefOrGetter<number | null>,
): {
  liveTime: Ref<string | null>;
  liveDate: Ref<string | null>;
  liveDateTime: Ref<string | null>;
  liveDateIso: Ref<string | null>;
} {
  const liveTime = ref<string | null>(null);
  const liveDate = ref<string | null>(null);
  const liveDateTime = ref<string | null>(null);
  const liveDateIso = ref<string | null>(null);
  let timer: ReturnType<typeof setInterval> | null = null;
  let baseUnixtime: number | null = null;
  let basePerfNow = 0;

  function syncAnchor(): void {
    const anchor = anchorUnixtime ? toValue(anchorUnixtime) : null;
    if (anchor !== null) {
      baseUnixtime = anchor;
      basePerfNow = performance.now();
    } else {
      baseUnixtime = null;
      basePerfNow = 0;
    }
  }

  function currentUnixtime(): number | null {
    if (baseUnixtime === null) {
      return null;
    }
    const elapsed = (performance.now() - basePerfNow) / 1000;
    return baseUnixtime + elapsed;
  }

  function update(): void {
    const offset = toValue(offsetHours);
    if (offset === null) {
      liveTime.value = null;
      liveDate.value = null;
      liveDateTime.value = null;
      liveDateIso.value = null;
      return;
    }

    const fmt = toValue(format);
    const unixtime = currentUnixtime();

    if (unixtime !== null) {
      liveTime.value =
        fmt === "datetime"
          ? formatLiveLocalDateTimeFromUnix(unixtime, offset)
          : fmt === "time-seconds"
            ? formatLiveLocalTimeWithSecondsFromUnix(unixtime, offset)
            : fmt === "date"
              ? formatLiveLocalDateFromUnix(unixtime, offset)
              : formatLiveLocalTimeFromUnix(unixtime, offset);
      liveDate.value = formatLiveLocalDateFromUnix(unixtime, offset);
      liveDateTime.value = isoDateTimeFromUnix(unixtime, offset);
      liveDateIso.value = isoDateFromUnix(unixtime, offset);
      return;
    }

    liveTime.value =
      fmt === "datetime"
        ? formatLiveLocalDateTime(offset)
        : fmt === "time-seconds"
          ? formatLiveLocalTimeWithSeconds(offset)
          : fmt === "date"
            ? formatLiveLocalDate(offset)
            : formatLiveLocalTime(offset);
    liveDate.value = formatLiveLocalDate(offset);
    liveDateTime.value = isoDateTimeFromOffset(offset);
    liveDateIso.value = isoDateFromOffset(offset);
  }

  onMounted(() => {
    syncAnchor();
    update();
    timer = setInterval(update, 1_000);
  });

  onUnmounted(() => {
    if (timer) {
      clearInterval(timer);
    }
  });

  watch(
    () =>
      [
        toValue(offsetHours),
        toValue(format),
        anchorUnixtime ? toValue(anchorUnixtime) : null,
      ] as const,
    () => {
      syncAnchor();
      update();
    },
  );

  return { liveTime, liveDate, liveDateTime, liveDateIso };
}
