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
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
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

const {
  data: resumeApi,
  loading: resumeLoading,
  fetch: fetchResume,
} = useCachedApi<ResumeData>("/resume");
const {
  data: donations,
  loading: donationsLoading,
  fetch: fetchDonations,
} = useCachedApi<DonationsConfig>("/donations/config");
const { playback, isVisible } = useSpotifyNowPlaying();
const apiError = ref(false);
const donationsError = ref(false);
const donationsFetched = ref(false);
const donationsStarted = ref(false);
const contactModal = ref<"inquiry" | "feedback" | null>(null);
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

async function loadDonations(): Promise<void> {
  donationsStarted.value = true;
  donationsError.value = false;
  try {
    await fetchDonations();
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    donationsError.value = true;
  } finally {
    donationsFetched.value = true;
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
      void loadDonations();
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
  <div class="portfolio-cv" :aria-busy="resumeLoading && !resumeApi">
    <div v-if="apiError" class="mx-auto max-w-5xl px-6 pt-4 print:hidden">
      <ErrorState
        message="Using cached portfolio data — live sync unavailable."
        show-retry
        retry-label="retry sync"
        @retry="loadResume"
      />
    </div>

    <SectionWrapper width="full">
      <HeroBlock
        :name="resume.name"
        :title="resume.title"
        :tagline="resume.tagline"
        :location="resume.location"
        :availability="resume.availability"
        :bio="resume.bio"
        @inquire="contactModal = 'inquiry'"
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
      <Suspense>
        <ExperienceList :experience="resume.experience" />
        <template #fallback>
          <div class="h-40 animate-pulse rounded-lg bg-surface-card" aria-hidden="true" />
        </template>
      </Suspense>
    </SectionWrapper>

    <SectionWrapper id="projects" title="projects" width="full" dark>
      <Suspense>
        <ProjectsGrid :projects="resume.projects" />
        <template #fallback>
          <div class="h-40 animate-pulse rounded-lg bg-surface-card" aria-hidden="true" />
        </template>
      </Suspense>
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
      <p class="text-body text-center mb-2">
        Open to full-time and contract — usually reply within 24h (EU timezone).
      </p>
      <p class="text-meta text-center mb-6">
        Fastest: Telegram or email. Or send a short inquiry below.
      </p>
      <div class="flex flex-wrap justify-center gap-4 mb-6">
        <button type="button" class="cta-primary print:hidden" @click="contactModal = 'inquiry'">
          send inquiry
        </button>
      </div>
      <div class="flex flex-wrap justify-center gap-4">
        <ContactLinkChip v-for="link in contactLinks" :key="link.id" :link="link" />
      </div>
      <div class="mt-6 flex justify-center print:hidden">
        <button
          type="button"
          class="text-meta text-surface-sage underline-offset-4 hover:underline inline-flex items-center gap-2 min-h-11 px-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
          @click="contactModal = 'feedback'"
        >
          <ContactIcon id="feedback" class="size-4 shrink-0" />
          send feedback instead
        </button>
      </div>
      <FeedbackModal
        v-if="contactModal"
        :intent="contactModal"
        @close="contactModal = null"
      />
    </SectionWrapper>

    <div ref="supportSectionRef" class="print:hidden">
      <SectionWrapper id="support" title="support my work" width="prose" dark alternate>
        <p class="text-body mb-6">
          If my tools or writing have helped you, a small contribution keeps the work going.
        </p>
        <div
          v-if="donationsStarted && donationsLoading"
          class="h-24 animate-pulse rounded-lg bg-surface-card"
          aria-busy="true"
        />
        <DonationsBlock v-else-if="donations" :config="donations" />
        <ErrorState
          v-else-if="donationsError"
          message="Donation options are temporarily unavailable."
          show-retry
          retry-label="retry"
          @retry="loadDonations"
        />
        <EmptyState
          v-else-if="donationsFetched"
          title="No donation options"
          description="Support options are not configured right now."
        />
      </SectionWrapper>
    </div>
  </div>
</template>
