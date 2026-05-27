<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";

import { useCachedApi } from "@/composables/useCachedApi";
import type { SpotifyNowPlaying } from "@/types";

const POLL_MS = 30_000;
const CACHE_TTL_MS = 30_000;

const { data: playback, fetch: fetchPlayback } = useCachedApi<SpotifyNowPlaying>(
  "/spotify/now-playing",
  CACHE_TTL_MS,
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
</script>

<template>
  <a
    v-if="playback?.enabled && playback.is_playing && playback.track_url"
    :href="playback.track_url"
    target="_blank"
    rel="noopener noreferrer"
    class="flex items-center gap-3 min-w-0 px-3 py-2 rounded-lg border border-surface-border bg-surface-card hover:border-accent-blue transition-colors group"
  >
    <BaseImage
      v-if="playback.album_art_url"
      :src="playback.album_art_url"
      :alt="`${playback.title} cover`"
      :lazy="false"
      class="w-10 h-10 rounded shrink-0"
      width="40"
      height="40"
    />
    <div class="min-w-0 flex-1">
      <div class="flex items-center gap-2 text-xs text-accent-blue mb-0.5">
        <span class="inline-flex items-end gap-0.5 h-3" aria-hidden="true">
          <span class="w-0.5 bg-accent-blue animate-pulse h-2" />
          <span class="w-0.5 bg-accent-blue animate-pulse h-3 [animation-delay:150ms]" />
          <span class="w-0.5 bg-accent-blue animate-pulse h-1.5 [animation-delay:300ms]" />
        </span>
        <span>Listening on Spotify</span>
      </div>
      <p class="text-sm text-surface-light font-semibold truncate group-hover:text-accent-blue transition-colors">
        {{ playback.title }}
      </p>
      <p class="text-xs text-surface-mid truncate">
        {{ playback.artist }}
      </p>
    </div>
  </a>
</template>
