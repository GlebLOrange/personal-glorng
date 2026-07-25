<script setup lang="ts">
import { computed, ref, useTemplateRef } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import CollapsibleUsageGuide from "@/components/ui/CollapsibleUsageGuide.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { api } from "@/composables/useApi";
import { useToolbarOptionsPopover } from "@/composables/useToolbarOptionsPopover";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessageFromBlob } from "@/types/api";

const url = ref("");
const format = ref("best");
const audioOnly = ref(false);
const loading = ref(false);
const optionsOpen = ref(false);
const optionsRoot = useTemplateRef<HTMLElement>("optionsRoot");
const optionsPanel = useTemplateRef<HTMLElement>("optionsPanel");
const optionsTrigger = useTemplateRef<InstanceType<typeof ToolbarPillButton>>("optionsTrigger");
const { toast } = useNotify();

const { toggle: toggleOptions } = useToolbarOptionsPopover({
  open: optionsOpen,
  rootRef: optionsRoot,
  panelRef: optionsPanel,
  triggerRef: optionsTrigger,
});

const formats = [
  { value: "best", label: "best (auto)" },
  { value: "bestvideo+bestaudio/best", label: "best video + audio" },
  { value: "bestvideo[height<=1080]+bestaudio/best", label: "1080p max" },
  { value: "bestvideo[height<=720]+bestaudio/best", label: "720p max" },
  { value: "bestaudio/best", label: "best audio" },
];

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
      <div class="mb-3 flex w-full min-w-0 flex-wrap items-center gap-2">
        <div
          ref="optionsRoot"
          class="relative inline-flex"
          :class="optionsOpen ? 'z-40' : undefined"
        >
          <ToolbarPillButton
            ref="optionsTrigger"
            family="1xx"
            type="button"
            :selected="optionsOpen || hasCustomOptions"
            aria-haspopup="dialog"
            :aria-expanded="optionsOpen"
            aria-controls="vid-download-options-dialog"
            @click.stop="toggleOptions"
          >
            options
            <span v-if="optionsActiveLabel" class="text-surface-muted">
              · {{ optionsActiveLabel }}
            </span>
            <ChevronIcon :open="optionsOpen" />
          </ToolbarPillButton>

          <div
            v-if="optionsOpen"
            id="vid-download-options-dialog"
            ref="optionsPanel"
            role="dialog"
            aria-labelledby="vid-download-options-title"
            tabindex="-1"
            class="absolute left-0 top-full z-10 mt-1 w-max min-w-[16rem] max-w-[min(100vw-2rem,24rem)] space-y-3 rounded-lg border border-surface-border bg-surface-card p-3 shadow-lg"
            @click.stop
          >
            <h2 id="vid-download-options-title" class="sr-only">download options</h2>

            <BaseSelect
              id="vid-download-quality"
              v-model="format"
              compact
              aria-label="quality"
            >
              <option v-for="f in formats" :key="f.value" :value="f.value">
                {{ f.label }}
              </option>
            </BaseSelect>

            <label class="flex cursor-pointer items-center gap-2 text-sm text-surface-mid">
              <input
                v-model="audioOnly"
                type="checkbox"
                name="audio_only"
                class="accent-accent-blue"
              />
              audio only
            </label>
          </div>
        </div>

        <ToolbarPillButton
          family="2xx"
          type="submit"
          class="ml-auto"
          :disabled="loading || !url.trim()"
        >
          {{ loading ? "downloading..." : "download" }}
        </ToolbarPillButton>
      </div>

      <BaseInput
        v-model="url"
        placeholder="url (https://....)"
        class="w-full"
      />
    </form>

    <CollapsibleUsageGuide title="yt-dlp usage guide">
      <div class="space-y-4 text-sm text-surface-light">
        <div>
          <h3 class="mb-2 font-bold text-accent-blue">Format selection</h3>
          <p class="mb-1 text-surface-mid">
            The <code class="text-accent-blue">-f</code> flag controls quality. Common values:
          </p>
          <ul class="ml-2 list-inside list-disc space-y-1 text-surface-mid">
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
            <code class="text-surface-light">-x --audio-format mp3</code> under the hood. Great for
            downloading music or podcast episodes.
          </p>
        </div>

        <div>
          <h3 class="mb-2 font-bold text-accent-blue">Limits</h3>
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
          class="inline-block text-accent-blue transition-colors hover:text-accent-blue/80"
        >
          Full yt-dlp documentation &rarr;
        </a>
      </div>
    </CollapsibleUsageGuide>
  </PageShell>
</template>
