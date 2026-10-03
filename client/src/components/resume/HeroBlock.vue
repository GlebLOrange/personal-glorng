<script setup lang="ts">
import { ref } from "vue";

import LocationIcon from "@/components/icons/LocationIcon.vue";
import { useNotify } from "@/composables/useNotify";
import { PORTFOLIO_SECTION_LINKS } from "@/constants/portfolioSections";
import { getApiErrorMessageFromBlob } from "@/types/api";

const CV_FILENAME = "gleb.y.cv.pdf";

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
    const { api } = await import("@/composables/useApi");
    const response = await api.get<Blob>("/resume/pdf", {
      responseType: "blob",
      headers: { Accept: "application/pdf" },
    });
    const contentType = String(
      response.headers["content-type"] ?? response.data.type ?? "",
    ).toLowerCase();
    if (!contentType.includes("application/pdf")) {
      throw new Error("CV download did not return a PDF");
    }

    const url = URL.createObjectURL(response.data);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = CV_FILENAME;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    const message = await getApiErrorMessageFromBlob(err, "Failed to download CV");
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
    <h1 class="text-4xl sm:text-5xl md:text-6xl font-bold mb-3 text-balance">
      <span class="accent-gradient">{{ name }}</span>
    </h1>
    <p class="text-2xl md:text-3xl text-surface-light mb-2">{{ title }}</p>
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
      <span v-if="location && availability" class="inline-flex min-h-11 items-center" aria-hidden="true"
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

    <div class="mt-6 flex flex-col sm:flex-row flex-wrap items-center justify-center gap-2 print:hidden">
      <button type="button" class="cta-primary" @click="emit('inquire')">get in touch</button>
      <button
        type="button"
        class="cta-secondary"
        :disabled="isDownloadingCv"
        @click="downloadCv"
      >
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
        class="ml-1 underline underline-offset-4 text-accent-blue hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
        @click="printPage"
      >
        print page instead
      </button>
    </p>

    <!-- Mobile: disclosure. md+: light middot rail (sticky section nav covers scroll). -->
    <div class="portfolio-link-rail mt-5 print:hidden">
      <details class="md:hidden group mx-auto max-w-xs text-left">
        <summary
          class="nav-link flex min-h-11 cursor-pointer list-none items-center justify-center rounded-lg px-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 [&::-webkit-details-marker]:hidden"
        >
          jump to…
        </summary>
        <nav aria-label="On this page" class="mt-2">
          <ul class="m-0 flex list-none flex-col items-stretch gap-1 p-0">
            <li v-for="link in PORTFOLIO_SECTION_LINKS" :key="link.href">
              <a
                :href="link.href"
                class="nav-link flex min-h-11 items-center justify-center rounded-lg px-3"
              >
                {{ link.label }}
              </a>
            </li>
          </ul>
        </nav>
      </details>

      <nav aria-label="On this page" class="hidden md:block">
        <ul class="m-0 flex list-none flex-wrap items-center justify-center gap-y-1 p-0">
          <li
            v-for="(link, i) in PORTFOLIO_SECTION_LINKS"
            :key="link.href"
            class="inline-flex items-center"
          >
            <span v-if="i > 0" class="px-1.5 text-surface-muted" aria-hidden="true">·</span>
            <a
              :href="link.href"
              class="nav-link inline-flex min-h-11 items-center px-1 rounded-lg"
            >
              {{ link.label }}
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>
