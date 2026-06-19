<script setup lang="ts">
import { computed } from "vue";

import type { SpotifyNowPlaying } from "@/types";

const props = defineProps<{
  playback?: SpotifyNowPlaying | null;
  fallbackSrc?: string;
  height?: number;
}>();

const embedSrc = computed(() => {
  if (!props.playback?.track_url) {
    return props.fallbackSrc ?? "";
  }

  try {
    const url = new URL(props.playback.track_url);
    const [, type, id] = url.pathname.split("/");
    if (url.hostname !== "open.spotify.com" || type !== "track" || !id) {
      return "";
    }

    return `https://open.spotify.com/embed/track/${id}?utm_source=generator&theme=0`;
  } catch {
    return "";
  }
});

const embedTitle = computed(() => {
  const track = props.playback?.title ?? "featured track";
  const artist = props.playback?.artist ? ` by ${props.playback.artist}` : "";
  return `Spotify now playing: ${track}${artist}`;
});
</script>

<template>
  <iframe
    v-if="embedSrc"
    data-testid="embed-iframe"
    class="block w-full rounded-xl border-0"
    :src="embedSrc"
    width="100%"
    :height="height ?? 152"
    frameborder="0"
    allowfullscreen
    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
    loading="lazy"
    :title="embedTitle"
  />
</template>
