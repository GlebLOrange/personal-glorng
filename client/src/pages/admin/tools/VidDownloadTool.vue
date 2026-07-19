<script setup lang="ts">
import { ref } from "vue";

import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessageFromBlob } from "@/types/api";

const url = ref("");
const format = ref("best");
const audioOnly = ref(false);
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
  } catch (err) {
    const msg = await getApiErrorMessageFromBlob(err, "Download failed");
    toast(msg, "error");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <PageShell
    title="vid-download"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'vid' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
    <form class="space-y-4 mb-8" @submit.prevent="download">
      <div class="flex items-start gap-2">
        <BaseInput
          v-model="url"
          placeholder="youtube url (https://www.youtube.com/watch?v=...)"
          aria-label="youtube url (https://www.youtube.com/watch?v=...)"
          class="min-w-0 flex-1"
        />
        <BaseButton
          type="submit"
          variant="primary"
          size="field"
          :disabled="loading || !url.trim()"
        >
          {{ loading ? "downloading..." : "download" }}
        </BaseButton>
      </div>

      <BaseSelect v-model="format">
          <option v-for="f in formats" :key="f.value" :value="f.value">
            {{ f.label }}
          </option>
      </BaseSelect>

      <label class="flex items-center gap-2 text-sm text-surface-mid cursor-pointer">
        <input v-model="audioOnly" type="checkbox" class="accent-accent-blue" />
        audio only (extract as MP3)
      </label>
    </form>

    <button
      class="text-sm text-accent-blue hover:text-accent-violet transition-colors mb-4"
      @click="guideOpen = !guideOpen"
    >
      {{ guideOpen ? "▾ Hide" : "▸ Show" }} yt-dlp usage guide
    </button>

    <Card v-if="guideOpen">
      <div class="text-surface-light text-sm space-y-4">
        <div>
          <h3 class="text-accent-blue font-bold mb-2">Format selection</h3>
          <p class="text-surface-mid mb-1">
            The <code class="text-accent-blue">-f</code> flag controls quality. Common values:
          </p>
          <ul class="list-disc list-inside text-surface-mid space-y-1 ml-2">
            <li><code class="text-surface-light">best</code> -- best single file (default)</li>
            <li>
              <code class="text-surface-light">bestvideo+bestaudio/best</code> -- merge best streams
              (needs ffmpeg)
            </li>
            <li>
              <code class="text-surface-light">bestvideo[height&lt;=720]+bestaudio</code> -- cap at
              720p
            </li>
            <li><code class="text-surface-light">bestaudio</code> -- audio stream only</li>
          </ul>
        </div>

        <div>
          <h3 class="text-accent-blue font-bold mb-2">Supported sites</h3>
          <p class="text-surface-mid">
            This public tool accepts YouTube URLs only (youtube.com, youtu.be, m.youtube.com, and
            music.youtube.com). Other hosts are rejected for security and abuse prevention.
          </p>
        </div>

        <div>
          <h3 class="text-accent-blue font-bold mb-2">Audio extraction</h3>
          <p class="text-surface-mid">
            Check "Audio only" to extract the audio track as MP3. This uses
            <code class="text-surface-light">-x --audio-format mp3</code> under the hood. Great for
            downloading music or podcast episodes.
          </p>
        </div>

        <div>
          <h3 class="text-accent-blue font-bold mb-2">Limits</h3>
          <p class="text-surface-mid">
            Downloads are limited to 500 MB and 2 minutes per request. Each IP may run one download
            at a time, with at most two concurrent downloads across the server. Public use is also
            rate limited to five downloads per hour per IP.
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
    </Card>
  </PageShell>
</template>
