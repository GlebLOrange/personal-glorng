<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, onUnmounted, ref } from "vue";

import ContactLinkChip from "@/components/contact/ContactLinkChip.vue";
import FeedbackModal from "@/components/feedback/FeedbackModal.vue";
import SectionWrapper from "@/components/layout/SectionWrapper.vue";
import EducationList from "@/components/resume/EducationList.vue";
import GitHubReposStrip from "@/components/resume/GitHubReposStrip.vue";
import HeroBlock from "@/components/resume/HeroBlock.vue";
import PortfolioGlance from "@/components/resume/PortfolioGlance.vue";
import SkillsGrid from "@/components/resume/SkillsGrid.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import { useCachedApi } from "@/composables/useCachedApi";
import { buildContactLinks } from "@/constants/contactMeta";
import { RESUME_FALLBACK } from "@/constants/resumeFallback";
import type { PublicGitHubRepo, ResumeData } from "@/types";

/** ponytail: hide a one-card gallery — looks thin without a peer */
const MIN_GITHUB_STRIP_REPOS = 2;

const ExperienceList = defineAsyncComponent(() => import("@/components/resume/ExperienceList.vue"));
const CaseStudies = defineAsyncComponent(() => import("@/components/resume/CaseStudies.vue"));

const {
  data: resumeApi,
  loading: resumeLoading,
  fetch: fetchResume,
} = useCachedApi<ResumeData>("/resume");
const apiError = ref(false);
const contactModal = ref<"inquiry" | null>(null);
/** Filled via GET /github/repos when /resume returned a cold-cache empty strip. */
const githubReposExtra = ref<PublicGitHubRepo[] | null>(null);
let cancelGithubIdle: (() => void) | null = null;

const resume = computed(() => resumeApi.value ?? RESUME_FALLBACK);
const contactLinks = computed(() => buildContactLinks(resume.value.links));
const education = computed(() => resume.value.education ?? []);
const githubProfileUrl = computed(() => resume.value.links.github);
const highlightedRepos = computed(() => {
  const fromResume = resume.value.github?.repos ?? [];
  const repos = fromResume.length > 0 ? fromResume : (githubReposExtra.value ?? []);
  const profileLogin = resume.value.github?.username?.toLowerCase() ?? "";
  const publicRepos = repos.filter((repo) => {
    if (repo.fork || repo.private) return false;
    // GitHub profile README repo is not an engineering sample.
    if (profileLogin && repo.name.toLowerCase() === profileLogin) return false;
    return true;
  });
  // Hide a one-card gallery — looks thin without a peer.
  if (publicRepos.length < MIN_GITHUB_STRIP_REPOS) {
    return [];
  }
  return publicRepos.slice(0, 4);
});

async function loadResume(): Promise<void> {
  apiError.value = false;
  try {
    await fetchResume();
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    apiError.value = true;
  }
}

function runWhenIdle(task: () => void): () => void {
  if (typeof window !== "undefined" && "requestIdleCallback" in window) {
    const id = window.requestIdleCallback(() => task(), { timeout: 2500 });
    return () => window.cancelIdleCallback(id);
  }
  const id = globalThis.setTimeout(task, 0);
  return () => globalThis.clearTimeout(id);
}

async function loadGithubReposIfNeeded(): Promise<void> {
  if ((resume.value.github?.repos.length ?? 0) > 0) return;
  try {
    const { api } = await import("@/composables/useApi");
    const { data } = await api.get<PublicGitHubRepo[]>("/github/repos");
    githubReposExtra.value = data;
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
  }
}

onMounted(() => {
  void loadResume().then(() => {
    cancelGithubIdle = runWhenIdle(() => {
      void loadGithubReposIfNeeded();
    });
  });
});

onUnmounted(() => {
  cancelGithubIdle?.();
  cancelGithubIdle = null;
});
</script>

<template>
  <div class="portfolio-cv" :aria-busy="resumeLoading && !resumeApi">
    <div v-if="apiError" class="mx-auto max-w-5xl px-6 pt-4 print:hidden">
      <ErrorState
        message="Using cached portfolio data — live sync unavailable."
        show-retry
        retry-label="retry sync"
        retry-icon="sync"
        @retry="loadResume"
      />
    </div>

    <SectionWrapper width="full">
      <div class="relative isolate overflow-hidden">
        <div
          class="pointer-events-none absolute inset-0 -z-10 print:hidden"
          aria-hidden="true"
        >
          <img
            src="/brand/welcome-bg.webp"
            alt=""
            class="absolute inset-0 h-full w-full object-cover object-center opacity-50 [html[data-theme=dark]_&]:opacity-85"
            width="1280"
            height="720"
            decoding="async"
          />
          <!-- Center veil keeps the name AA; the photo stays visible toward the edges -->
          <div
            class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,var(--color-surface-dark)_0%,transparent_72%)]"
          />
          <div
            class="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-surface-dark to-transparent"
          />
        </div>
        <HeroBlock
          :name="resume.name"
          :title="resume.title"
          :tagline="resume.tagline"
          :location="resume.location"
          :availability="resume.availability"
          @inquire="contactModal = 'inquiry'"
        />
      </div>
    </SectionWrapper>

    <SectionWrapper id="about" title="about" width="full" alternate>
      <PortfolioGlance :resume="resume" />
      <p class="text-body mb-4 mt-6 max-w-3xl text-pretty">
        {{ resume.bio }}
      </p>
      <p v-if="resume.hiring_note" class="text-body mb-6 max-w-3xl">
        {{ resume.hiring_note }}
      </p>
      <div v-if="highlightedRepos.length" class="mt-2 print:hidden">
        <GitHubReposStrip :repos="highlightedRepos" :profile-url="githubProfileUrl" />
      </div>
    </SectionWrapper>

    <SectionWrapper id="experience" title="experience" width="full">
      <Suspense>
        <ExperienceList :experience="resume.experience" />
        <template #fallback>
          <div class="h-40 animate-pulse rounded-lg bg-surface-card" aria-hidden="true" />
        </template>
      </Suspense>
    </SectionWrapper>

    <SectionWrapper id="case-studies" title="case studies" width="full" alternate>
      <Suspense>
        <CaseStudies :projects="resume.projects" />
        <template #fallback>
          <div class="h-40 animate-pulse rounded-lg bg-surface-card" aria-hidden="true" />
        </template>
      </Suspense>
    </SectionWrapper>

    <SectionWrapper id="skills" title="skills" width="full">
      <SkillsGrid :skills="resume.skills" />
    </SectionWrapper>

    <SectionWrapper
      v-if="education.length > 0"
      id="education"
      title="education"
      width="prose"
    >
      <EducationList :education="education" />
    </SectionWrapper>

    <SectionWrapper
      id="contacts"
      title="contacts"
      width="full"
      :alternate="education.length > 0"
    >
      <p class="text-body mb-3 max-w-2xl">
        open to full-time and contract — usually reply within 24h (EU timezone)
      </p>
      <p class="text-meta mb-6 flex flex-wrap items-center gap-x-2 gap-y-2">
        <span>fastest: telegram or email. or</span>
        <button type="button" class="cta-primary print:hidden" @click="contactModal = 'inquiry'">
          send inquiry
        </button>
      </p>
      <div class="flex flex-wrap gap-4">
        <ContactLinkChip v-for="link in contactLinks" :key="link.id" :link="link" />
      </div>
    </SectionWrapper>

    <!-- Sync import + page-root mount: first CTA click opens without async delay -->
    <FeedbackModal
      :open="contactModal === 'inquiry'"
      intent="inquiry"
      @close="contactModal = null"
    />
  </div>
</template>
