<script setup lang="ts">
import { computed, defineAsyncComponent, nextTick, onMounted, onUnmounted, ref } from "vue";

import ContactIcon from "@/components/contact/ContactIcon.vue";
import ContactLinkChip from "@/components/contact/ContactLinkChip.vue";
import SectionWrapper from "@/components/layout/SectionWrapper.vue";
import EducationList from "@/components/resume/EducationList.vue";
import HeroBlock from "@/components/resume/HeroBlock.vue";
import NowPlayingEmbed from "@/components/resume/NowPlayingEmbed.vue";
import PortfolioGlance from "@/components/resume/PortfolioGlance.vue";
import SkillsGrid from "@/components/resume/SkillsGrid.vue";
import { useCachedApi } from "@/composables/useCachedApi";
import { useSpotifyNowPlaying } from "@/composables/useSpotifyNowPlaying";
import { buildContactLinks } from "@/constants/contactMeta";
import { RESUME_FALLBACK } from "@/constants/resumeFallback";
import type { DonationsConfig, ResumeData } from "@/types";

const ExperienceList = defineAsyncComponent(
  () => import("@/components/resume/ExperienceList.vue"),
);
const ProjectsGrid = defineAsyncComponent(() => import("@/components/resume/ProjectsGrid.vue"));
const DonationsBlock = defineAsyncComponent(
  () => import("@/components/donations/DonationsBlock.vue"),
);
const FeedbackModal = defineAsyncComponent(() => import("@/components/feedback/FeedbackModal.vue"));

const { data: resumeApi, fetch: fetchResume } = useCachedApi<ResumeData>("/resume");
const { data: donations, fetch: fetchDonations } =
  useCachedApi<DonationsConfig>("/donations/config");
const { playback, isVisible } = useSpotifyNowPlaying();
const apiError = ref(false);
const showFeedback = ref(false);
const supportSectionRef = ref<HTMLElement | null>(null);
let supportObserver: IntersectionObserver | null = null;

const resume = computed(() => resumeApi.value ?? RESUME_FALLBACK);
const contactLinks = computed(() => buildContactLinks(resume.value.links));
const education = computed(() => resume.value.education ?? []);

async function loadResume(): Promise<void> {
  apiError.value = false;
  try {
    await fetchResume();
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    apiError.value = true;
  }
}

function observeSupportSection(): void {
  if (supportObserver || !supportSectionRef.value) {
    return;
  }

  supportObserver = new IntersectionObserver(
    (entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) {
        return;
      }
      supportObserver?.disconnect();
      supportObserver = null;
      void fetchDonations().catch((err) => {
        if (import.meta.env.DEV) console.error(err);
      });
    },
    { rootMargin: "200px 0px" },
  );
  supportObserver.observe(supportSectionRef.value);
}

onMounted(() => {
  void loadResume();
  void nextTick(() => observeSupportSection());
});

onUnmounted(() => {
  supportObserver?.disconnect();
  supportObserver = null;
});
</script>

<template>
  <div class="portfolio-cv">
    <p
      v-if="apiError"
      class="mx-auto max-w-5xl px-6 pt-4 text-label text-accent-golden print:hidden"
      role="status"
    >
      Using cached portfolio data — live sync unavailable.
    </p>

    <SectionWrapper width="full">
      <HeroBlock
        :name="resume.name"
        :title="resume.title"
        :tagline="resume.tagline"
        :location="resume.location"
        :availability="resume.availability"
        :bio="resume.bio"
        :contact-links="contactLinks"
      >
        <template #after-actions>
          <NowPlayingEmbed
            v-if="isVisible"
            :playback="playback"
            :height="80"
            class="max-w-md mx-auto mt-8 print:hidden"
          />
        </template>
      </HeroBlock>
    </SectionWrapper>

    <SectionWrapper id="about" title="about" width="full" dark alternate>
      <PortfolioGlance :resume="resume" />
    </SectionWrapper>

    <SectionWrapper id="skills" title="skills" width="full" dark>
      <SkillsGrid :skills="resume.skills" />
    </SectionWrapper>

    <SectionWrapper id="experience" title="experience" width="prose" dark alternate>
      <ExperienceList :experience="resume.experience" />
    </SectionWrapper>

    <SectionWrapper id="projects" title="projects" width="full" dark>
      <ProjectsGrid :projects="resume.projects" />
    </SectionWrapper>

    <SectionWrapper
      v-if="education.length > 0"
      id="education"
      title="education"
      width="prose"
      dark
      alternate
    >
      <EducationList :education="education" />
    </SectionWrapper>

    <SectionWrapper id="contact" title="contact" width="prose" dark :alternate="education.length === 0">
      <div class="flex flex-wrap justify-center gap-4">
        <ContactLinkChip v-for="link in contactLinks" :key="link.id" :link="link" />
        <button
          type="button"
          class="interactive-surface inline-flex items-center gap-2 px-5 py-3 text-base text-surface-sage min-h-11 print:hidden"
          @click="showFeedback = true"
        >
          <ContactIcon id="feedback" class="size-4 shrink-0" />
          send feedback
        </button>
      </div>
      <FeedbackModal v-if="showFeedback" @close="showFeedback = false" />
    </SectionWrapper>

    <div ref="supportSectionRef" class="print:hidden">
      <SectionWrapper id="support" title="support my work" width="prose" dark alternate>
        <p class="text-body mb-6">
          If my tools or writing have helped you, a small contribution keeps the work going.
        </p>
        <DonationsBlock v-if="donations" :config="donations" />
      </SectionWrapper>
    </div>
  </div>
</template>
