<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import ContactIcon from "@/components/contact/ContactIcon.vue";
import ContactLinkChip from "@/components/contact/ContactLinkChip.vue";
import DonationsBlock from "@/components/donations/DonationsBlock.vue";
import FeedbackModal from "@/components/feedback/FeedbackModal.vue";
import PortfolioSearchChat from "@/components/search/PortfolioSearchChat.vue";
import SectionWrapper from "@/components/layout/SectionWrapper.vue";
import EducationList from "@/components/resume/EducationList.vue";
import ExperienceList from "@/components/resume/ExperienceList.vue";
import HeroBlock from "@/components/resume/HeroBlock.vue";
import PortfolioGlance from "@/components/resume/PortfolioGlance.vue";
import ProjectsGrid from "@/components/resume/ProjectsGrid.vue";
import SkillsGrid from "@/components/resume/SkillsGrid.vue";
import { useCachedApi } from "@/composables/useCachedApi";
import { buildContactLinks } from "@/constants/contactMeta";
import { RESUME_FALLBACK } from "@/constants/resumeFallback";
import type { DonationsConfig, ResumeData } from "@/types";
import { isAiSearchEnabled } from "@/utils/featureFlags";

const { data: resumeApi, fetch: fetchResume } = useCachedApi<ResumeData>("/resume");
const { data: donations, fetch: fetchDonations } =
  useCachedApi<DonationsConfig>("/donations/config");
const apiError = ref(false);
const showFeedback = ref(false);

const resume = computed(() => resumeApi.value ?? RESUME_FALLBACK);
const contactLinks = computed(() => buildContactLinks(resume.value.links));
const education = computed(() => resume.value.education ?? []);

async function loadResume(): Promise<void> {
  apiError.value = false;
  try {
    await Promise.all([fetchResume(), fetchDonations()]);
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    apiError.value = true;
  }
}

onMounted(loadResume);
</script>

<template>
  <div class="portfolio-cv">
    <p
      v-if="apiError"
      class="max-w-5xl mx-auto px-6 pt-4 text-label text-accent-golden print:hidden"
      role="status"
    >
      Using cached portfolio data — live sync unavailable.
    </p>

    <SectionWrapper>
      <HeroBlock
        :name="resume.name"
        :title="resume.title"
        :tagline="resume.tagline"
        :location="resume.location"
        :availability="resume.availability"
        :bio="resume.bio"
        :contact-links="contactLinks"
      />
    </SectionWrapper>

    <SectionWrapper id="about" title="about" dark alternate>
      <PortfolioGlance :resume="resume" />
    </SectionWrapper>

    <SectionWrapper id="skills" title="skills" dark>
      <SkillsGrid :skills="resume.skills" />
    </SectionWrapper>

    <SectionWrapper id="experience" title="experience" dark alternate>
      <ExperienceList :experience="resume.experience" />
    </SectionWrapper>

    <SectionWrapper id="projects" title="projects" dark>
      <ProjectsGrid :projects="resume.projects" />
    </SectionWrapper>

    <SectionWrapper
      v-if="education.length > 0"
      id="education"
      title="education"
      dark
      alternate
    >
      <EducationList :education="education" />
    </SectionWrapper>

    <SectionWrapper id="contact" title="contact" dark :alternate="education.length === 0">
      <div class="flex flex-wrap gap-4">
        <ContactLinkChip v-for="link in contactLinks" :key="link.id" :link="link" />
        <button
          type="button"
          class="interactive-surface inline-flex items-center gap-2 px-5 py-3 text-base text-surface-sage min-h-11 print:hidden"
          @click="showFeedback = true"
        >
          <ContactIcon id="feedback" class="size-4 shrink-0" />
          Send Feedback
        </button>
      </div>
      <FeedbackModal v-if="showFeedback" @close="showFeedback = false" />
    </SectionWrapper>

    <div class="print:hidden">
      <SectionWrapper id="support" title="support" dark alternate>
        <p class="text-body mb-6">If you find my work useful, consider supporting me.</p>
        <DonationsBlock v-if="donations" :config="donations" />
      </SectionWrapper>
    </div>

    <PortfolioSearchChat v-if="isAiSearchEnabled()" />
  </div>
</template>
