import { onMounted, onUnmounted, ref, watch, type MaybeRefOrGetter, type Ref, toValue } from "vue";

import {
  formatLiveLocalDate,
  formatLiveLocalDateFromIana,
  formatLiveLocalDateTime,
  formatLiveLocalFromIana,
  formatLiveLocalTime,
  formatLiveLocalTimeWithSeconds,
  isoDateFromIana,
  isoDateFromOffset,
  isoDateTimeFromIana,
  isoDateTimeFromOffset,
  type LiveTimeFormatKind,
} from "@/utils/weather";

/** Tick every second with IANA timezone or UTC offset wall clock. */
export function useLiveLocalTime(
  offsetHours: MaybeRefOrGetter<number | null>,
  format: MaybeRefOrGetter<LiveTimeFormatKind> = "datetime",
  _anchorUnixtime?: MaybeRefOrGetter<number | null>,
  ianaTimezone?: MaybeRefOrGetter<string | null>,
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

  function update(): void {
    const fmt = toValue(format);
    const iana = ianaTimezone ? toValue(ianaTimezone) : null;

    if (iana) {
      const now = new Date();
      liveTime.value = formatLiveLocalFromIana(iana, fmt, now);
      liveDate.value = formatLiveLocalDateFromIana(iana, now);
      liveDateTime.value = isoDateTimeFromIana(iana, now);
      liveDateIso.value = isoDateFromIana(iana, now);
      return;
    }

    const offset = toValue(offsetHours);
    if (offset === null) {
      liveTime.value = null;
      liveDate.value = null;
      liveDateTime.value = null;
      liveDateIso.value = null;
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
        ianaTimezone ? toValue(ianaTimezone) : null,
      ] as const,
    () => {
      update();
    },
  );

  return { liveTime, liveDate, liveDateTime, liveDateIso };
}
