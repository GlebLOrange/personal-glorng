<script setup lang="ts">
import { computed, ref } from "vue";

import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import LocationIcon from "@/components/icons/LocationIcon.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessageFromBlob } from "@/types/api";

const CV_FILENAME = "gleb.y.cv.pdf";
const HANDBOOK_URL = "https://gleblorange.github.io/portfolio-glorng/";
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
  <div class="py-12 md:py-20 text-center">
    <h1 class="text-4xl sm:text-5xl md:text-6xl font-bold mb-4 text-balance">
      <span class="accent-gradient">{{ name }}</span>
    </h1>
    <p class="text-2xl md:text-3xl text-surface-sage mb-2 lowercase">{{ title }}</p>
    <p v-if="tagline" class="text-lg text-accent-blue mb-4 text-pretty max-w-2xl mx-auto">
      {{ tagline }}
    </p>
    <p
      v-if="location || availability"
      class="text-meta mb-6 flex flex-wrap items-center justify-center gap-x-3 gap-y-1"
    >
      <span v-if="location" class="inline-flex items-center gap-1.5">
        <LocationIcon class-name="size-3.5 shrink-0" />
        {{ location }}
      </span>
      <span v-if="location && availability" aria-hidden="true">·</span>
      <a
        v-if="availability"
        href="#contacts"
        class="text-meta underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded lowercase"
      >
        {{ availability }}
      </a>
    </p>
    <p
      class="text-lg md:text-xl max-w-2xl mx-auto text-surface-sage leading-relaxed text-pretty lowercase"
    >
      {{ bio }}
    </p>

    <div class="mt-8 flex flex-col sm:flex-row flex-wrap justify-center gap-2 print:hidden">
      <ToolbarPillButton family="2xx" type="button" @click="emit('inquire')">
        get in touch
      </ToolbarPillButton>
      <ToolbarPillButton family="1xx" type="button" :disabled="isDownloadingCv" @click="downloadCv">
        {{ isDownloadingCv ? "downloading…" : "download cv" }}
      </ToolbarPillButton>
    </div>

    <nav
      class="mt-4 flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-sm text-surface-sage print:hidden"
      aria-label="engineering proof links"
    >
      <a
        v-for="link in proofLinks"
        :key="link.href"
        :href="link.href"
        :target="link.external ? '_blank' : undefined"
        :rel="link.external ? 'noopener noreferrer' : undefined"
        class="underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded lowercase"
      >
        {{ link.label }}
        <span v-if="link.external" class="sr-only">(opens in new tab)</span>
      </a>
    </nav>

    <slot name="after-actions" />
  </div>
</template>
