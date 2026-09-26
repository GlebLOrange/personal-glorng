<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";

import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { Card } from "@/components/ui/card";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";

type QrErrorLevel = "L" | "M" | "Q" | "H";

interface QrGenerateResponse {
  content_preview: string;
  label: string | null;
  error_level: QrErrorLevel;
  svg: string;
}

const content = ref("");
const label = ref("");
const errorLevel = ref<QrErrorLevel>("M");
const generated = ref<QrGenerateResponse | null>(null);
const previewUrl = ref("");

const { loading: creating, run: runCreate } = useApiAction();

const canCreate = computed(() => Boolean(content.value.trim()) && !creating.value);

function setPreviewFromSvg(svg: string): void {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
  previewUrl.value = URL.createObjectURL(new Blob([svg], { type: "image/svg+xml" }));
}

watch(
  () => generated.value?.svg,
  (svg) => {
    if (svg) setPreviewFromSvg(svg);
    else if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value);
      previewUrl.value = "";
    }
  },
);

onBeforeUnmount(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
});

async function createQr(): Promise<void> {
  if (!content.value.trim()) return;
  const result = await runCreate(
    () =>
      api.post<QrGenerateResponse>("/tools/qr-generator", {
        content: content.value.trim(),
        label: label.value.trim() || null,
        error_level: errorLevel.value,
      }),
    { successMessage: "QR code generated", errorFallback: "Failed to generate QR code" },
  );
  if (result) {
    generated.value = result.data;
  }
}

function downloadSvg(): void {
  const svg = generated.value?.svg;
  if (!svg) return;
  const url = URL.createObjectURL(new Blob([svg], { type: "image/svg+xml" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "qr-code.svg";
  anchor.click();
  URL.revokeObjectURL(url);
}

const previewAlt = computed(
  () => generated.value?.label || generated.value?.content_preview || "QR code preview",
);
</script>

<template>
  <PageShell
    title="qr generator"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'qr generator' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
    <p class="mb-4 text-sm text-surface-mid">
      Codes are generated in your browser session only — nothing is saved on the server. Download
      the SVG before you leave if you need it later.
    </p>

    <div class="grid min-w-0 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,280px)]">
      <Card variant="ghost" class="min-w-0">
        <form class="space-y-3" @submit.prevent="createQr">
          <label class="block text-sm text-surface-mid">
            payload
            <textarea
              v-model="content"
              rows="4"
              maxlength="2000"
              placeholder="URL, text, Wi‑Fi string, etc."
              class="mt-1 w-full resize-y rounded-md border border-surface-border bg-surface-base px-3 py-2 text-sm text-surface-high focus:border-accent focus:outline-none"
            />
          </label>
          <div class="flex flex-wrap gap-3">
            <BaseInput
              v-model="label"
              label="label (optional)"
              placeholder="My link"
              class="min-w-0 flex-1"
              maxlength="120"
            />
            <label class="block text-sm text-surface-mid">
              error correction
              <select
                v-model="errorLevel"
                class="mt-1 block w-full rounded-md border border-surface-border bg-surface-base px-3 py-2 text-sm"
              >
                <option value="L">L (~7%)</option>
                <option value="M">M (~15%)</option>
                <option value="Q">Q (~25%)</option>
                <option value="H">H (~30%)</option>
              </select>
            </label>
          </div>
          <BaseButton variant="primary" type="submit" :disabled="!canCreate">
            {{ creating ? "generating…" : "generate qr" }}
          </BaseButton>
        </form>
      </Card>

      <Card variant="ghost" class="flex min-h-[280px] flex-col items-center justify-center gap-3 p-4">
        <img
          v-if="previewUrl"
          :src="previewUrl"
          :alt="previewAlt"
          class="max-h-64 max-w-full rounded-md bg-white p-2"
        />
        <p v-else class="text-center text-sm text-surface-mid">
          Generate a code to preview it here.
        </p>
        <button
          v-if="generated?.svg"
          type="button"
          class="text-sm text-accent hover:underline"
          @click="downloadSvg"
        >
          download svg
        </button>
      </Card>
    </div>
  </PageShell>
</template>
