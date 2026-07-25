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

type TickFn = () => void;

const subscribers = new Set<TickFn>();
let sharedTimer: ReturnType<typeof setInterval> | null = null;
let visibilityBound = false;

function tickAll(): void {
  for (const fn of subscribers) {
    fn();
  }
}

function stopSharedTimer(): void {
  if (sharedTimer === null) {
    return;
  }
  clearInterval(sharedTimer);
  sharedTimer = null;
}

function startSharedTimer(): void {
  if (sharedTimer !== null) {
    return;
  }
  if (typeof document !== "undefined" && document.hidden) {
    return;
  }
  sharedTimer = setInterval(tickAll, 1_000);
}

function onVisibilityChange(): void {
  if (typeof document === "undefined") {
    return;
  }
  if (document.hidden) {
    stopSharedTimer();
    return;
  }
  if (subscribers.size === 0) {
    return;
  }
  tickAll();
  startSharedTimer();
}

function ensureVisibilityListener(): void {
  if (visibilityBound || typeof document === "undefined") {
    return;
  }
  visibilityBound = true;
  document.addEventListener("visibilitychange", onVisibilityChange);
}

/** One shared 1Hz timer for all live clocks; paused while the tab is hidden. */
function subscribeLiveClock(tick: TickFn): () => void {
  subscribers.add(tick);
  ensureVisibilityListener();
  startSharedTimer();
  return () => {
    subscribers.delete(tick);
    if (subscribers.size === 0) {
      stopSharedTimer();
    }
  };
}

function updateFromOffset(
  offset: number,
  fmt: LiveTimeFormatKind,
  refs: {
    liveTime: Ref<string | null>;
    liveDate: Ref<string | null>;
    liveDateTime: Ref<string | null>;
    liveDateIso: Ref<string | null>;
  },
): void {
  refs.liveTime.value =
    fmt === "datetime"
      ? formatLiveLocalDateTime(offset)
      : fmt === "time-seconds"
        ? formatLiveLocalTimeWithSeconds(offset)
        : fmt === "date"
          ? formatLiveLocalDate(offset)
          : formatLiveLocalTime(offset);
  refs.liveDate.value = formatLiveLocalDate(offset);
  refs.liveDateTime.value = isoDateTimeFromOffset(offset);
  refs.liveDateIso.value = isoDateFromOffset(offset);
}

/** Tick every second with IANA timezone or UTC offset wall clock. */
export function useLiveLocalTime(
  offsetHours: MaybeRefOrGetter<number | null>,
  format: MaybeRefOrGetter<LiveTimeFormatKind> = "datetime",
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
  let unsubscribe: (() => void) | null = null;

  const refs = { liveTime, liveDate, liveDateTime, liveDateIso };

  function update(): void {
    const fmt = toValue(format);
    const iana = ianaTimezone ? toValue(ianaTimezone) : null;

    if (iana) {
      try {
        const now = new Date();
        liveTime.value = formatLiveLocalFromIana(iana, fmt, now);
        liveDate.value = formatLiveLocalDateFromIana(iana, now);
        liveDateTime.value = isoDateTimeFromIana(iana, now);
        liveDateIso.value = isoDateFromIana(iana, now);
        return;
      } catch {
        // ponytail: invalid IANA from upstream falls back to offset wall clock
      }
    }

    const offset = toValue(offsetHours);
    if (offset === null) {
      liveTime.value = null;
      liveDate.value = null;
      liveDateTime.value = null;
      liveDateIso.value = null;
      return;
    }

    updateFromOffset(offset, fmt, refs);
  }

  onMounted(() => {
    update();
    unsubscribe = subscribeLiveClock(update);
  });

  onUnmounted(() => {
    unsubscribe?.();
    unsubscribe = null;
  });

  watch(
    () =>
      [toValue(offsetHours), toValue(format), ianaTimezone ? toValue(ianaTimezone) : null] as const,
    () => {
      update();
    },
  );

  return { liveTime, liveDate, liveDateTime, liveDateIso };
}
