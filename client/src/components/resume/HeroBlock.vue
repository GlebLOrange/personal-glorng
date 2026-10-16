<script setup lang="ts">
import { ref } from "vue";

import LocationIcon from "@/components/icons/LocationIcon.vue";
import { useNotify } from "@/composables/useNotify";
import { downloadResumeExport, resumeDownloadErrorMessage } from "@/utils/resumeDownload";

defineProps<{
  name: string;
  title: string;
  tagline?: string;
  location?: string;
  availability?: string;
}>();

const emit = defineEmits<{ inquire: [] }>();

const isDownloadingCv = ref(false);
const showPrintFallback = ref(false);
const { toast } = useNotify();

async function downloadCv(): Promise<void> {
  if (isDownloadingCv.value) return;
  isDownloadingCv.value = true;
  showPrintFallback.value = false;
  try {
    await downloadResumeExport("pdf");
  } catch (err) {
    const message = await resumeDownloadErrorMessage(err, "Failed to download CV");
    // ponytail: no static PDF — offer print only when the user chooses it
    toast(message, "error");
    showPrintFallback.value = true;
  } finally {
    isDownloadingCv.value = false;
  }
}

function printPage(): void {
  window.print();
}
</script>

<template>
  <div class="py-12 md:py-16 text-center">
    <p class="mb-2 text-lg font-medium tracking-tight text-surface-light sm:text-xl">{{ name }}</p>
    <h1 class="mb-3 text-balance text-2xl font-bold tracking-tight text-surface-light sm:text-3xl md:text-4xl">
      {{ title }}
    </h1>
    <p v-if="tagline" class="text-lg text-surface-sage mb-3 text-pretty max-w-2xl mx-auto">
      {{ tagline }}
    </p>
    <p
      v-if="location || availability"
      class="text-meta mb-4 flex flex-wrap items-center justify-center gap-x-3 gap-y-1"
    >
      <span v-if="location" class="inline-flex min-h-11 items-center gap-1.5">
        <LocationIcon class-name="size-3.5 shrink-0" />
        {{ location }}
      </span>
      <span
        v-if="location && availability"
        class="hidden sm:inline-flex min-h-11 items-center"
        aria-hidden="true"
        >·</span
      >
      <a
        v-if="availability"
        href="#contacts"
        class="inline-flex min-h-11 items-center px-1 text-meta underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
      >
        {{ availability }}
      </a>
    </p>

    <div
      class="mt-6 flex flex-col sm:flex-row flex-wrap items-center justify-center gap-2 print:hidden"
    >
      <button type="button" class="cta-hero" @click="emit('inquire')">get in touch</button>
      <button type="button" class="cta-secondary" :disabled="isDownloadingCv" @click="downloadCv">
        {{ isDownloadingCv ? "downloading…" : "download cv" }}
      </button>
    </div>

    <p v-if="showPrintFallback" class="mt-3 text-meta print:hidden" role="status">
      PDF unavailable.
      <button
        type="button"
        class="ml-1 underline underline-offset-4 text-accent-blue hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
        @click="printPage"
      >
        print page instead
      </button>
    </p>
  </div>
</template>
