<script setup lang="ts">
import ContactIcon from "@/components/contact/ContactIcon.vue";
import type { ContactLink } from "@/constants/contactMeta";

defineProps<{
  name: string;
  title: string;
  tagline?: string;
  location?: string;
  availability?: string;
  bio: string;
  contactLinks?: ContactLink[];
}>();
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
      <a href="/api/resume/pdf" class="cta-secondary" download>Download CV</a>
    </div>
  </div>
</template>
