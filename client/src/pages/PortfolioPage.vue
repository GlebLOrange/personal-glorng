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
const latestRole = computed(() => resume.value.experience.slice(0, 1));
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
      <HeroBlock
        layout="status-rail"
        :name="resume.name"
        :title="resume.title"
        :tagline="resume.tagline"
        :location="resume.location"
        :availability="resume.availability"
        sample-note="this site is the sample"
        @inquire="contactModal = 'inquiry'"
      />
    </SectionWrapper>

    <SectionWrapper id="about" title="about" width="full" label-tone="primary">
      <div class="max-w-prose space-y-4 text-pretty">
        <p class="text-body">
          {{ resume.bio }}
        </p>
        <p v-if="resume.hiring_note" class="text-body">
          {{ resume.hiring_note }}
        </p>
      </div>
      <div class="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2 lg:items-start">
        <div class="min-w-0">
          <PortfolioGlance :resume="resume" />
        </div>
        <div v-if="latestRole.length" class="min-w-0">
          <p class="text-label text-accent-coral mb-3">latest role</p>
          <Suspense>
            <ExperienceList :experience="latestRole" />
            <template #fallback>
              <div class="h-40 animate-pulse rounded-lg bg-surface-card" aria-hidden="true" />
            </template>
          </Suspense>
        </div>
      </div>
      <div v-if="highlightedRepos.length" class="mt-6 print:hidden">
        <GitHubReposStrip :repos="highlightedRepos" :profile-url="githubProfileUrl" />
      </div>
    </SectionWrapper>

    <SectionWrapper id="experience" title="experience" width="full" label-tone="tertiary">
      <Suspense>
        <ExperienceList :experience="resume.experience" />
        <template #fallback>
          <div class="h-40 animate-pulse rounded-lg bg-surface-card" aria-hidden="true" />
        </template>
      </Suspense>
    </SectionWrapper>

    <SectionWrapper id="case-studies" title="case studies" width="full" label-tone="secondary">
      <Suspense>
        <CaseStudies :projects="resume.projects" />
        <template #fallback>
          <div class="h-40 animate-pulse rounded-lg bg-surface-card" aria-hidden="true" />
        </template>
      </Suspense>
    </SectionWrapper>

    <SectionWrapper id="skills" title="skills" width="full" label-tone="custom">
      <SkillsGrid :skills="resume.skills" />
    </SectionWrapper>

    <SectionWrapper
      v-if="education.length > 0"
      id="education"
      title="education"
      width="prose"
      label-tone="secondary"
    >
      <EducationList :education="education" />
    </SectionWrapper>

    <SectionWrapper id="contacts" title="contacts" width="full" label-tone="error">
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
