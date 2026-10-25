<script setup lang="ts">
import { computed, defineAsyncComponent, nextTick, onMounted, onUnmounted, ref } from "vue";

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
import { colorThemeResolved } from "@/composables/useColorTheme";
import { buildContactLinks } from "@/constants/contactMeta";
import { PORTFOLIO_SECTION_LINKS } from "@/constants/portfolioSections";
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
const heroSentinelRef = ref<HTMLElement | null>(null);
const showSectionNav = ref(false);
const sectionNavTop = ref(72);
/** Filled via GET /github/repos when /resume returned a cold-cache empty strip. */
const githubReposExtra = ref<PublicGitHubRepo[] | null>(null);
let heroObserver: IntersectionObserver | null = null;
let cancelGithubIdle: (() => void) | null = null;

const resume = computed(() => resumeApi.value ?? RESUME_FALLBACK);
/** Portfolio hero decoration only — not used on /profile (shared HeroBlock). */
const welcomeBgSrc = computed(() =>
  colorThemeResolved.value === "light"
    ? "/brand/welcome-bg-light.svg"
    : "/brand/welcome-bg.svg",
);
const contactLinks = computed(() => buildContactLinks(resume.value.links));
const education = computed(() => resume.value.education ?? []);
/** Sticky in-page nav — drop education when that section is empty. */
const sectionLinks = computed(() =>
  PORTFOLIO_SECTION_LINKS.filter(
    (link) => link.href !== "#education" || education.value.length > 0,
  ),
);
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

function syncSectionNavTop(): void {
  const header = document.getElementById("site-header");
  sectionNavTop.value = header?.offsetHeight ?? 72;
}

function observeHeroSentinel(): void {
  if (heroObserver || !heroSentinelRef.value) {
    return;
  }
  syncSectionNavTop();
  heroObserver = new IntersectionObserver(
    (entries) => {
      const entry = entries[0];
      if (!entry) return;
      // Show sticky section nav once the hero leaves the top of the viewport.
      showSectionNav.value = !entry.isIntersecting;
    },
    { rootMargin: `-${sectionNavTop.value}px 0px 0px 0px`, threshold: 0 },
  );
  heroObserver.observe(heroSentinelRef.value);
}

onMounted(() => {
  void loadResume().then(() => {
    cancelGithubIdle = runWhenIdle(() => {
      void loadGithubReposIfNeeded();
    });
  });
  void nextTick(() => {
    observeHeroSentinel();
  });
});

onUnmounted(() => {
  cancelGithubIdle?.();
  cancelGithubIdle = null;
  heroObserver?.disconnect();
  heroObserver = null;
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

    <!-- v-if (not opacity/invisible): avoids a fixed overlay intercepting hero CTA taps -->
    <div
      v-if="showSectionNav"
      class="pointer-events-none fixed inset-x-0 z-30 flex justify-center px-4 print:hidden"
      :style="{ top: `${sectionNavTop}px` }"
    >
      <nav
        class="pointer-events-auto max-w-5xl rounded-b-lg border border-t-0 border-surface-border/60 bg-surface-dark/90 px-3 py-1 backdrop-blur-md"
        aria-label="On this page"
      >
        <ul class="m-0 flex list-none flex-wrap items-center justify-center gap-y-0 p-0">
          <li
            v-for="(link, i) in sectionLinks"
            :key="link.href"
            class="inline-flex items-center"
          >
            <span v-if="i > 0" class="px-1.5 text-surface-muted" aria-hidden="true">·</span>
            <a
              :href="link.href"
              class="nav-link inline-flex min-h-11 items-center px-1 rounded-lg text-sm"
            >
              {{ link.label }}
            </a>
          </li>
        </ul>
      </nav>
    </div>

    <SectionWrapper width="full">
      <div ref="heroSentinelRef" class="relative isolate overflow-hidden">
        <div
          class="pointer-events-none absolute inset-0 -z-10 print:hidden"
          aria-hidden="true"
        >
          <img
            :src="welcomeBgSrc"
            alt=""
            class="absolute inset-y-0 right-0 h-full w-[min(100%,42rem)] max-w-none object-contain object-right opacity-90"
            width="800"
            height="420"
            decoding="async"
          />
          <!-- Scrim keeps hero copy AA against the faint lockup -->
          <div
            class="absolute inset-0 bg-gradient-to-r from-surface-dark via-surface-dark/85 to-surface-dark/40"
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
      <p class="text-body mb-4 max-w-3xl text-pretty">
        {{ resume.bio }}
      </p>
      <p v-if="resume.hiring_note" class="text-body mb-6 max-w-3xl">
        {{ resume.hiring_note }}
      </p>
      <PortfolioGlance :resume="resume" />
      <div v-if="highlightedRepos.length" class="mt-8 print:hidden">
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
