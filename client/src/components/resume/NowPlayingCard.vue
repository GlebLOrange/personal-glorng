<script setup lang="ts">
import { computed } from "vue";

import BaseCard from "@/components/ui/BaseCard.vue";
import type { SpotifyNowPlaying } from "@/types";

const props = defineProps<{
  playback: SpotifyNowPlaying;
}>();

const progressPercent = computed(() => {
  const p = props.playback;
  if (!p.progress_ms || !p.duration_ms || p.duration_ms <= 0) {
    return 0;
  }
  return Math.min(100, (p.progress_ms / p.duration_ms) * 100);
});
</script>

<template>
  <a
    v-if="playback.track_url"
    :href="playback.track_url"
    target="_blank"
    rel="noopener noreferrer"
    class="block group"
  >
    <BaseCard hoverable class="!p-0 overflow-hidden">
      <div class="px-4 pt-3 pb-1 text-xs uppercase tracking-wider text-surface-mid font-mono">
        spotify --now
      </div>

      <div class="flex flex-col sm:flex-row gap-4 p-4 pt-2">
        <div class="shrink-0 flex justify-center sm:justify-start">
          <img
            v-if="playback.album_art_url"
            :src="playback.album_art_url"
            :alt="`${playback.title ?? 'Track'} cover`"
            class="w-20 h-20 sm:w-24 sm:h-24 rounded-lg object-cover ring-2 ring-accent-blue/30 animate-pulse"
            width="96"
            height="96"
          />
        </div>

        <div class="min-w-0 flex-1 flex flex-col justify-center">
          <div class="flex items-center gap-2 text-xs text-accent-blue mb-2">
            <span class="inline-flex items-end gap-0.5 h-3" aria-hidden="true">
              <span class="w-0.5 bg-accent-blue animate-pulse h-2" />
              <span class="w-0.5 bg-accent-blue animate-pulse h-3 [animation-delay:150ms]" />
              <span class="w-0.5 bg-accent-blue animate-pulse h-1.5 [animation-delay:300ms]" />
            </span>
            <span>Now playing</span>
          </div>

          <p
            class="text-lg font-bold text-surface-light truncate group-hover:text-accent-blue transition-colors"
          >
            {{ playback.title }}
          </p>
          <p class="text-sm text-surface-mid truncate">
            {{ playback.artist }}
          </p>
          <p v-if="playback.album" class="text-xs text-surface-mid/80 truncate mt-0.5">
            {{ playback.album }}
          </p>

          <div
            v-if="playback.progress_ms != null && playback.duration_ms"
            class="mt-3 h-1 rounded-full bg-surface-border overflow-hidden"
            role="progressbar"
            :aria-valuenow="playback.progress_ms"
            :aria-valuemin="0"
            :aria-valuemax="playback.duration_ms"
          >
            <div
              class="h-full bg-gradient-to-r from-accent-blue to-accent-violet transition-all duration-300"
              :style="{ width: `${progressPercent}%` }"
            />
          </div>

          <p class="mt-3 text-xs text-accent-blue group-hover:text-accent-violet transition-colors">
            Open in Spotify &rarr;
          </p>
        </div>
      </div>
    </BaseCard>
  </a>
</template>
