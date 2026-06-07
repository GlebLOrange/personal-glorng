<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import ContactIcon from "@/components/contact/ContactIcon.vue";
import ContactLinkChip from "@/components/contact/ContactLinkChip.vue";
import DonationsBlock from "@/components/donations/DonationsBlock.vue";
import FeedbackModal from "@/components/feedback/FeedbackModal.vue";
import PortfolioSearchChat from "@/components/search/PortfolioSearchChat.vue";
import SectionWrapper from "@/components/layout/SectionWrapper.vue";
import ExperienceList from "@/components/resume/ExperienceList.vue";
import HeroBlock from "@/components/resume/HeroBlock.vue";
import ProjectsGrid from "@/components/resume/ProjectsGrid.vue";
import SkillsGrid from "@/components/resume/SkillsGrid.vue";
import CodeBlock from "@/components/ui/CodeBlock.vue";
import { useCachedApi } from "@/composables/useCachedApi";
import { buildContactLinks } from "@/constants/contactMeta";
import { RESUME_FALLBACK } from "@/constants/resumeFallback";
import type { DonationsConfig, ResumeData } from "@/types";

const { data: resumeApi, fetch: fetchResume } = useCachedApi<ResumeData>("/resume");
const { data: donations, fetch: fetchDonations } =
  useCachedApi<DonationsConfig>("/donations/config");
const apiError = ref(false);
const showFeedback = ref(false);

const resume = computed(() => resumeApi.value ?? RESUME_FALLBACK);
const contactLinks = computed(() => buildContactLinks(resume.value.links));

async function loadResume(): Promise<void> {
  apiError.value = false;
  try {
    await Promise.all([fetchResume(), fetchDonations()]);
  } catch (err) {
    console.error(err);
    apiError.value = true;
  }
}

onMounted(loadResume);
</script>

<template>
  <div>
    <p v-if="apiError" class="max-w-5xl mx-auto px-6 pt-4 text-xs text-accent-golden" role="status">
      Using cached portfolio data — live sync unavailable.
    </p>

    <SectionWrapper>
      <HeroBlock :name="resume.name" :title="resume.title" :bio="resume.bio" />
    </SectionWrapper>

    <!-- Spotify now-playing disabled until Premium subscription is available -->

    <SectionWrapper id="about" title="about" dark>
      <CodeBlock title="whoami">{{ resume.bio }}</CodeBlock>
    </SectionWrapper>

    <SectionWrapper id="skills" title="skills" dark>
      <SkillsGrid :skills="resume.skills" />
    </SectionWrapper>

    <SectionWrapper id="experience" title="experience" dark>
      <ExperienceList :experience="resume.experience" />
    </SectionWrapper>

    <SectionWrapper id="projects" title="projects" dark>
      <ProjectsGrid :projects="resume.projects" />
    </SectionWrapper>

    <SectionWrapper id="support" title="support" dark>
      <p class="text-surface-mid mb-6 text-sm">
        If you find my work useful, consider supporting me.
      </p>
      <DonationsBlock v-if="donations" :config="donations" />
    </SectionWrapper>

    <SectionWrapper id="contact" title="contact" dark>
      <div class="flex flex-wrap gap-4">
        <ContactLinkChip v-for="link in contactLinks" :key="link.id" :link="link" />
        <button
          type="button"
          class="interactive-surface inline-flex items-center gap-2 px-4 py-2 text-sm text-surface-mid"
          @click="showFeedback = true"
        >
          <ContactIcon id="feedback" class="size-4 shrink-0" />
          Send Feedback
        </button>
      </div>
      <FeedbackModal v-if="showFeedback" @close="showFeedback = false" />
    </SectionWrapper>

    <PortfolioSearchChat />
  </div>
</template>
