<script setup lang="ts">
import { ref } from "vue";

import ContactIcon from "@/components/contact/ContactIcon.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import type { ContactLink } from "@/constants/contactMeta";
import { getApiErrorMessageFromBlob } from "@/types/api";

const CV_FILENAME = "gleb.y.cv.pdf";

defineProps<{
  name: string;
  title: string;
  tagline?: string;
  location?: string;
  availability?: string;
  bio: string;
  contactLinks?: ContactLink[];
}>();

const isDownloadingCv = ref(false);
const { toast } = useNotify();

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
    toast(message, "error");
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
    <p class="text-2xl md:text-3xl text-surface-sage mb-2">{{ title }}</p>
    <p v-if="tagline" class="text-lg text-accent-blue mb-4 text-pretty max-w-2xl mx-auto">
      {{ tagline }}
    </p>
    <p
      v-if="location || availability"
      class="text-meta mb-6 flex flex-wrap justify-center gap-x-3 gap-y-1"
    >
      <span v-if="location">{{ location }}</span>
      <span v-if="location && availability" aria-hidden="true">·</span>
      <span v-if="availability" class="text-accent-golden">{{ availability }}</span>
    </p>
    <p class="text-lg md:text-xl max-w-2xl mx-auto text-surface-sage leading-relaxed text-pretty">
      {{ bio }}
    </p>

    <div
      v-if="contactLinks?.length"
      class="mt-6 flex flex-wrap justify-center gap-3 print:hidden"
    >
      <a
        v-for="link in contactLinks"
        :key="link.id"
        :href="link.href"
        :aria-label="link.label"
        target="_blank"
        rel="noopener noreferrer"
        class="interactive-surface inline-flex items-center justify-center size-11 text-surface-sage"
      >
        <ContactIcon :id="link.id" class="size-5 shrink-0" />
      </a>
    </div>

    <div class="mt-8 flex flex-col sm:flex-row flex-wrap justify-center gap-4 print:hidden">
      <a href="#experience" class="cta-primary"> Experience </a>
      <a href="#projects" class="cta-secondary"> Projects </a>
      <a href="#contact" class="cta-secondary"> Contact </a>
      <button type="button" class="cta-secondary" :disabled="isDownloadingCv" @click="downloadCv">
        {{ isDownloadingCv ? "Downloading..." : "Download CV" }}
      </button>
    </div>

    <slot name="after-actions" />
  </div>
</template>
