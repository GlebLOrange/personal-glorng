import { computed, onMounted, onUnmounted, type ComputedRef, type Ref } from "vue";

import { useCachedApi } from "@/composables/useCachedApi";
import type { SpotifyNowPlaying } from "@/types";

const POLL_MS = 30_000;
const CACHE_TTL_MS = 30_000;

export function useSpotifyNowPlaying(): {
  playback: Ref<SpotifyNowPlaying | null>;
  isVisible: ComputedRef<boolean>;
  fetchPlayback: () => Promise<void>;
} {
  const { data: playback, fetch: fetchPlayback } = useCachedApi<SpotifyNowPlaying>(
    "/spotify/now-playing",
    CACHE_TTL_MS,
  );

  const isVisible = computed(() =>
    Boolean(playback.value?.enabled && playback.value.is_playing && playback.value.track_url),
  );

  let pollTimer: ReturnType<typeof setInterval> | null = null;

  onMounted(() => {
    void fetchPlayback();
    pollTimer = setInterval(() => {
      void fetchPlayback();
    }, POLL_MS);
  });

  onUnmounted(() => {
    if (pollTimer) {
      clearInterval(pollTimer);
    }
  });

  return { playback, isVisible, fetchPlayback };
}
