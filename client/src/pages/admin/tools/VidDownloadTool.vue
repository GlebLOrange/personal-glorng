<script setup lang="ts">
import { ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";

const url = ref("");
const format = ref("best");
const audioOnly = ref(false);
const extraArgs = ref("");
const loading = ref(false);
const guideOpen = ref(false);
const { toast } = useNotify();

const formats = [
  { value: "best", label: "Best (auto)" },
  { value: "bestvideo+bestaudio/best", label: "Best video + audio" },
  { value: "bestvideo[height<=1080]+bestaudio/best", label: "1080p max" },
  { value: "bestvideo[height<=720]+bestaudio/best", label: "720p max" },
  { value: "bestaudio/best", label: "Best audio" },
];

async function download(): Promise<void> {
  if (!url.value.trim()) return;
  loading.value = true;
  try {
    const resp = await api.post(
      "/tools/vid-download",
      {
        url: url.value,
        format: format.value,
        audio_only: audioOnly.value,
        extra_args: extraArgs.value || null,
      },
      { responseType: "blob" },
    );

    const disposition = resp.headers["content-disposition"] ?? "";
    const match = disposition.match(/filename="?(.+?)"?$/);
    const filename = match?.[1] ?? "download";

    const blob = new Blob([resp.data]);
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);

    toast("Download complete", "success");
  } catch (err: any) {
    let msg = "Download failed";
    if (err.response?.data) {
      try {
        const text = await err.response.data.text();
        const json = JSON.parse(text);
        msg = json.detail ?? msg;
      } catch (err) {
        console.error(err);
        // blob couldn't be parsed
      }
    }
    toast(msg, "error");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <AdminPageLayout title="vid-download">
    <form class="space-y-4 mb-8" @submit.prevent="download">
      <BaseInput
        v-model="url"
        placeholder="https://example.com/video"
        label="Video URL"
      />

      <div class="flex flex-col gap-1">
        <label class="text-sm text-surface-mid font-mono">Format</label>
        <select
          v-model="format"
          class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light font-mono text-sm
                 focus:outline-none focus:border-accent-blue transition-colors"
        >
          <option
            v-for="f in formats"
            :key="f.value"
            :value="f.value"
          >
            {{ f.label }}
          </option>
        </select>
      </div>

      <label class="flex items-center gap-2 text-sm text-surface-mid font-mono cursor-pointer">
        <input
          v-model="audioOnly"
          type="checkbox"
          class="accent-accent-blue"
        />
        Audio only (extract as MP3)
      </label>

      <BaseInput
        v-model="extraArgs"
        placeholder="--sub-langs en --write-thumbnail ..."
        label="Extra arguments (optional)"
      />

      <BaseButton variant="primary" :disabled="loading || !url.trim()">
        {{ loading ? "Downloading..." : "Download" }}
      </BaseButton>
    </form>

    <button
      class="text-sm text-accent-blue hover:text-accent-violet transition-colors mb-4 font-mono"
      @click="guideOpen = !guideOpen"
    >
      {{ guideOpen ? "▾ Hide" : "▸ Show" }} yt-dlp usage guide
    </button>

    <BaseCard v-if="guideOpen">
      <div class="text-surface-light text-sm space-y-4 font-mono">
        <div>
          <h3 class="text-accent-blue font-bold mb-2">Format selection</h3>
          <p class="text-surface-mid mb-1">
            The <code class="text-accent-blue">-f</code> flag controls quality. Common values:
          </p>
          <ul class="list-disc list-inside text-surface-mid space-y-1 ml-2">
            <li><code class="text-surface-light">best</code> -- best single file (default)</li>
            <li><code class="text-surface-light">bestvideo+bestaudio/best</code> -- merge best streams (needs ffmpeg)</li>
            <li><code class="text-surface-light">bestvideo[height&lt;=720]+bestaudio</code> -- cap at 720p</li>
            <li><code class="text-surface-light">bestaudio</code> -- audio stream only</li>
          </ul>
        </div>

        <div>
          <h3 class="text-accent-blue font-bold mb-2">Useful extra arguments</h3>
          <ul class="list-disc list-inside text-surface-mid space-y-1 ml-2">
            <li><code class="text-surface-light">--sub-langs en</code> -- embed English subtitles</li>
            <li><code class="text-surface-light">--write-thumbnail</code> -- save thumbnail alongside video</li>
            <li><code class="text-surface-light">--playlist-items 1-5</code> -- download first 5 items from a playlist</li>
            <li><code class="text-surface-light">--limit-rate 5M</code> -- limit download speed to 5 MB/s</li>
            <li><code class="text-surface-light">--sponsorblock-remove all</code> -- strip sponsor segments</li>
          </ul>
        </div>

        <div>
          <h3 class="text-accent-blue font-bold mb-2">Supported sites</h3>
          <p class="text-surface-mid">
            yt-dlp supports 1800+ sites including YouTube, Twitter/X, Instagram, TikTok,
            Reddit, Twitch, Vimeo, SoundCloud, and many more.
            Paste any video/audio URL and it will attempt to extract the media.
          </p>
        </div>

        <div>
          <h3 class="text-accent-blue font-bold mb-2">Audio extraction</h3>
          <p class="text-surface-mid">
            Check "Audio only" to extract the audio track as MP3. This uses
            <code class="text-surface-light">-x --audio-format mp3</code> under the hood.
            Great for downloading music or podcast episodes.
          </p>
        </div>

        <div>
          <h3 class="text-accent-blue font-bold mb-2">Security notes</h3>
          <p class="text-surface-mid">
            Some arguments are blocked for security: <code class="text-surface-light">-o</code>,
            <code class="text-surface-light">--exec</code>,
            <code class="text-surface-light">--batch-file</code>,
            <code class="text-surface-light">--cookies</code>, and similar flags
            that could affect the server filesystem. Downloads are limited to 2 minutes.
          </p>
        </div>

        <a
          href="https://github.com/yt-dlp/yt-dlp#readme"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-block text-accent-blue hover:text-accent-violet transition-colors"
        >
          Full yt-dlp documentation &rarr;
        </a>
      </div>
    </BaseCard>
  </AdminPageLayout>
</template>
