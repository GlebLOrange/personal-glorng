<script setup lang="ts">
import { onMounted, ref } from "vue";

import DonationsBlock from "@/components/donations/DonationsBlock.vue";
import FeedbackModal from "@/components/feedback/FeedbackModal.vue";
import SectionWrapper from "@/components/layout/SectionWrapper.vue";
import WeatherWidget from "@/components/weather/WeatherWidget.vue";
import ExperienceList from "@/components/resume/ExperienceList.vue";
import HeroBlock from "@/components/resume/HeroBlock.vue";
import NowPlayingCard from "@/components/resume/NowPlayingCard.vue";
import ProjectsGrid from "@/components/resume/ProjectsGrid.vue";
import SkillsGrid from "@/components/resume/SkillsGrid.vue";
import CodeBlock from "@/components/ui/CodeBlock.vue";
import { useCachedApi } from "@/composables/useCachedApi";
import { useSpotifyNowPlaying } from "@/composables/useSpotifyNowPlaying";
import { contactLinks } from "@/constants/links";
import type { DonationsConfig, ResumeData } from "@/types";

const { data: resume, fetch: fetchResume } = useCachedApi<ResumeData>("/resume");
const { data: donations, fetch: fetchDonations } = useCachedApi<DonationsConfig>("/donations/config");
const { playback, isVisible: showNowPlaying } = useSpotifyNowPlaying();
const error = ref(false);
const showFeedback = ref(false);

async function loadResume(): Promise<void> {
  error.value = false;
  try {
    await Promise.all([fetchResume(), fetchDonations()]);
  } catch (err) {
    console.error(err);
    error.value = true;
  }
}

onMounted(loadResume);
</script>

<template>
  <div v-if="resume">
    <div class="max-w-5xl mx-auto px-6 pt-4 flex justify-end">
      <WeatherWidget city="Wroclaw" compact />
    </div>

    <SectionWrapper>
      <HeroBlock :name="resume.name" :title="resume.title" :bio="resume.bio" />
    </SectionWrapper>

    <SectionWrapper v-if="showNowPlaying && playback" id="now-playing" title="now playing" dark>
      <NowPlayingCard :playback="playback" />
    </SectionWrapper>

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
        <a
          v-for="link in contactLinks"
          :key="link.label"
          :href="link.href"
          target="_blank"
          rel="noopener noreferrer"
          class="px-4 py-2 text-sm border border-surface-border rounded-lg text-surface-mid hover:border-accent-blue hover:text-accent-blue transition-colors"
        >
          {{ link.label }}
        </a>
        <button
          class="px-4 py-2 text-sm border border-surface-border rounded-lg text-surface-mid hover:border-accent-blue hover:text-accent-blue transition-colors"
          @click="showFeedback = true"
        >
          Send Feedback
        </button>
      </div>
      <FeedbackModal v-if="showFeedback" @close="showFeedback = false" />
    </SectionWrapper>
  </div>

  <div v-else-if="error" class="flex flex-col items-center justify-center min-h-[60vh] gap-4">
    <p class="text-surface-mid font-mono">Failed to load data.</p>
    <button
      class="px-4 py-2 text-sm border border-surface-border rounded-lg text-surface-mid hover:border-accent-blue hover:text-accent-blue transition-colors"
      @click="loadResume"
    >
      Retry
    </button>
  </div>

  <div v-else class="flex items-center justify-center min-h-[60vh]">
    <p class="text-surface-mid font-mono animate-pulse">Loading...</p>
  </div>
</template>
