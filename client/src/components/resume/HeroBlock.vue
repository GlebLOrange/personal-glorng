<script setup lang="ts">
import { computed, ref } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import DownloadIcon from "@/components/icons/DownloadIcon.vue";
import LocationIcon from "@/components/icons/LocationIcon.vue";
import { useNotify } from "@/composables/useNotify";
import { downloadResumeExport, resumeDownloadErrorMessage } from "@/utils/resumeDownload";

const props = withDefaults(
  defineProps<{
    name: string;
    title: string;
    tagline?: string;
    location?: string;
    availability?: string;
    /** Quiet third meta chip for the public status-rail hero. */
    sampleNote?: string;
    /** `status-rail` = public CV type scale + sample note; both layouts are centered. */
    layout?: "centered" | "status-rail";
  }>(),
  { layout: "centered" },
);

const emit = defineEmits<{ inquire: [] }>();

const isStatusRail = computed(() => props.layout === "status-rail");
const showMeta = computed(() =>
  Boolean(props.location || props.availability || (isStatusRail.value && props.sampleNote)),
);

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
    <p
      class="mb-2 font-medium tracking-tight text-surface-light"
      :class="isStatusRail ? 'text-3xl sm:text-4xl md:text-5xl' : 'text-xl sm:text-2xl md:text-3xl'"
    >
      {{ name }}
    </p>
    <h1
      class="mb-3 text-balance font-bold tracking-tight text-surface-light"
      :class="isStatusRail ? 'text-xl sm:text-2xl md:text-3xl' : 'text-2xl sm:text-3xl md:text-4xl'"
    >
      {{ title }}
    </h1>
    <p
      v-if="tagline && !isStatusRail"
      class="text-lg text-surface-sage mb-3 text-pretty max-w-2xl mx-auto"
    >
      {{ tagline }}
    </p>
    <p
      v-if="showMeta && isStatusRail"
      class="text-meta mb-4 flex flex-wrap items-center justify-center gap-x-3 gap-y-1"
    >
      <a
        v-if="availability"
        href="#contacts"
        class="inline-flex min-h-11 items-center px-1 text-meta underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50 rounded"
      >
        {{ availability }}
      </a>
      <span
        v-if="availability && location"
        class="hidden sm:inline-flex min-h-11 items-center"
        aria-hidden="true"
        >·</span
      >
      <span v-if="location" class="inline-flex min-h-11 items-center gap-1.5">
        <LocationIcon class-name="size-3.5 shrink-0" />
        {{ location }}
      </span>
      <template v-if="sampleNote">
        <span
          v-if="location || availability"
          class="hidden sm:inline-flex min-h-11 items-center"
          aria-hidden="true"
          >·</span
        >
        <span class="inline-flex min-h-11 items-center text-surface-sage">{{ sampleNote }}</span>
      </template>
    </p>
    <p
      v-else-if="showMeta"
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
        class="inline-flex min-h-11 items-center px-1 text-meta underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50 rounded"
      >
        {{ availability }}
      </a>
    </p>

    <div
      class="relative z-[45] mt-6 flex flex-col flex-wrap items-center justify-center gap-2 sm:flex-row print:hidden"
    >
      <button type="button" class="cta-hero inline-flex items-center gap-1.5" @click="emit('inquire')">
        <ChevronIcon class-name="size-3.5 shrink-0" />
        get in touch
      </button>
      <button
        type="button"
        class="cta-secondary inline-flex items-center gap-1.5"
        :disabled="isDownloadingCv"
        @click="downloadCv"
      >
        <DownloadIcon class-name="size-3.5 shrink-0" />
        {{ isDownloadingCv ? "downloading…" : "download cv" }}
      </button>
    </div>

    <p
      v-if="showPrintFallback"
      class="mt-3 text-meta print:hidden"
      role="status"
    >
      PDF unavailable.
      <button
        type="button"
        class="ml-1 inline-flex items-center gap-1 underline underline-offset-4 text-accent-coral hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50 rounded"
        @click="printPage"
      >
        <DownloadIcon class-name="size-3.5 shrink-0" />
        print page instead
      </button>
    </p>
  </div>
</template>
