<script setup lang="ts">
import { computed, ref } from "vue";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import CollapsibleUsageGuide from "@/components/ui/CollapsibleUsageGuide.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { familyBadgeClass } from "@/constants/httpStatusColors";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessageFromBlob } from "@/types/api";

const url = ref("");
const format = ref("best");
const audioOnly = ref(false);
const loading = ref(false);
const { toast } = useNotify();

const formats = [
  { value: "best", label: "best (auto)" },
  { value: "bestvideo+bestaudio/best", label: "best video + audio" },
  { value: "bestvideo[height<=1080]+bestaudio/best", label: "1080p max" },
  { value: "bestvideo[height<=720]+bestaudio/best", label: "720p max" },
  { value: "bestaudio/best", label: "best audio" },
];

const optionLabels = computed(() => [...formats.map((item) => item.label), "audio"]);

const hasCustomOptions = computed(() => audioOnly.value || format.value !== "best");

const optionsActiveLabel = computed(() => {
  const parts: string[] = [];
  const selected = formats.find((item) => item.value === format.value);
  if (selected && selected.value !== "best") parts.push(selected.label);
  if (audioOnly.value) parts.push("audio");
  return parts.length ? parts.join(" · ") : undefined;
});

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
    title="video downloader"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'video downloader' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
    <form class="mb-8 space-y-3" @submit.prevent="download">
      <CollapsibleUsageGuide title="yt-dlp usage guide">
        <template #start>
          <AdminFilterDropdown
            label="options"
            :show-clear="false"
            :has-active-filters="hasCustomOptions"
            :active-label="optionsActiveLabel"
            :option-labels="optionLabels"
          >
            <BaseSelect id="vid-download-quality" v-model="format" compact aria-label="quality">
              <option v-for="f in formats" :key="f.value" :value="f.value">
                {{ f.label }}
              </option>
            </BaseSelect>

            <AdminFilterChip
              label="audio only"
              :active="audioOnly"
              :color-class="familyBadgeClass('1xx')"
              @click="audioOnly = !audioOnly"
            />
          </AdminFilterDropdown>
        </template>
        <template #actions>
          <ToolbarPillButton family="2xx" type="submit" :disabled="loading || !url.trim()">
            {{ loading ? "downloading…" : "download" }}
          </ToolbarPillButton>
        </template>
        <div class="space-y-4 text-sm text-surface-light">
          <div>
            <h3 class="mb-2 font-bold text-accent-blue">Format selection</h3>
            <p class="mb-1 text-surface-mid">
              The <code class="text-accent-blue">-f</code> flag controls quality. Common values:
            </p>
            <ul class="ml-2 list-inside list-disc space-y-1 text-surface-mid">
              <li><code class="text-surface-light">best</code> -- best single file (default)</li>
              <li>
                <code class="text-surface-light">bestvideo+bestaudio/best</code> -- merge best
                streams (needs ffmpeg)
              </li>
              <li>
                <code class="text-surface-light">bestvideo[height&lt;=720]+bestaudio</code> -- cap
                at 720p
              </li>
              <li><code class="text-surface-light">bestaudio</code> -- audio stream only</li>
            </ul>
          </div>

          <div>
            <h3 class="mb-2 font-bold text-accent-blue">Supported sites</h3>
            <p class="text-surface-mid">
              This public tool accepts YouTube URLs only (youtube.com, youtu.be, m.youtube.com, and
              music.youtube.com). Other hosts are rejected for security and abuse prevention.
            </p>
          </div>

          <div>
            <h3 class="mb-2 font-bold text-accent-blue">Audio extraction</h3>
            <p class="text-surface-mid">
              Check "Audio only" to extract the audio track as MP3. This uses
              <code class="text-surface-light">-x --audio-format mp3</code> under the hood. Great
              for downloading music or podcast episodes.
            </p>
          </div>

          <div>
            <h3 class="mb-2 font-bold text-accent-blue">Limits</h3>
            <p class="text-surface-mid">
              Downloads are limited to 500 MB and 2 minutes per request. Each IP may run one
              download at a time, with at most two concurrent downloads across the server. Public
              use is also rate limited to five downloads per hour per IP.
            </p>
          </div>

          <a
            href="https://github.com/yt-dlp/yt-dlp#readme"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-block text-accent-blue transition-colors hover:text-accent-blue/80"
          >
            Full yt-dlp documentation &rarr;
          </a>
        </div>
      </CollapsibleUsageGuide>

      <BaseInput
        v-model="url"
        placeholder="url (example.com or https://…)"
        aria-label="url (example.com or https://…)"
        class="w-full"
      />
    </form>
  </PageShell>
</template>
