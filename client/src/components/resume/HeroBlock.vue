<script setup lang="ts">
import { computed, ref } from "vue";

import LocationIcon from "@/components/icons/LocationIcon.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { PORTFOLIO_SECTION_LINKS } from "@/constants/portfolioSections";
import { getApiErrorMessageFromBlob } from "@/types/api";

const CV_FILENAME = "gleb.y.cv.pdf";
const HANDBOOK_URL = "https://gleblorange.github.io/personal-glorng/";
const OPENAPI_PATH = "/api/docs";

const props = defineProps<{
  name: string;
  title: string;
  tagline?: string;
  location?: string;
  availability?: string;
  bio: string;
  githubUrl?: string;
  repoUrl?: string;
}>();

const emit = defineEmits<{ inquire: [] }>();

const isDownloadingCv = ref(false);
const { toast } = useNotify();

const proofLinks = computed(() => {
  const links: Array<{ href: string; label: string; external: boolean }> = [
    { href: HANDBOOK_URL, label: "architecture docs", external: true },
    { href: OPENAPI_PATH, label: "openapi", external: false },
  ];
  if (props.repoUrl) {
    links.unshift({ href: props.repoUrl, label: "source repo", external: true });
  } else if (props.githubUrl) {
    links.unshift({ href: props.githubUrl, label: "github", external: true });
  }
  return links;
});

async function downloadCv(): Promise<void> {
  if (isDownloadingCv.value) return;
  isDownloadingCv.value = true;
  try {
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
    // ponytail: no static PDF asset — print stylesheet is the offline fallback
    toast(`${message}. Opening print dialog as a fallback.`, "error");
    window.print();
  } finally {
    isDownloadingCv.value = false;
  }
}
</script>

<template>
  <div class="py-12 md:py-16">
    <h1 class="text-4xl sm:text-5xl md:text-6xl font-bold mb-3 text-balance">
      <span class="accent-gradient">{{ name }}</span>
    </h1>
    <p class="text-2xl md:text-3xl text-surface-sage mb-2">{{ title }}</p>
    <p v-if="tagline" class="text-lg text-accent-blue mb-3 text-pretty max-w-2xl">
      {{ tagline }}
    </p>
    <p
      v-if="location || availability"
      class="text-meta mb-4 flex flex-wrap items-center gap-x-3 gap-y-1"
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
    <p class="text-lg md:text-xl max-w-2xl text-surface-sage leading-relaxed text-pretty">
      {{ bio }}
    </p>

    <div class="mt-6 flex flex-col sm:flex-row flex-wrap gap-2 print:hidden">
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

    <!-- Jump + proof: middot lists, no eyebrows (labels live in aria-label). -->
    <div class="portfolio-link-rail mt-5 flex flex-col gap-1 print:hidden">
      <nav aria-label="On this page">
        <ul class="m-0 flex list-none flex-wrap items-center gap-y-1 p-0">
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
      <nav aria-label="site proof">
        <ul class="m-0 flex list-none flex-wrap items-center gap-y-1 p-0 text-sm">
          <li
            v-for="(link, i) in proofLinks"
            :key="link.href"
            class="inline-flex items-center"
          >
            <span v-if="i > 0" class="px-1.5 text-surface-muted" aria-hidden="true">·</span>
            <a
              :href="link.href"
              :target="link.external ? '_blank' : undefined"
              :rel="link.external ? 'noopener noreferrer' : undefined"
              class="nav-link inline-flex min-h-11 items-center px-1 rounded-lg text-surface-mid"
            >
              {{ link.label }}
              <span v-if="link.external" class="sr-only">(opens in new tab)</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>
