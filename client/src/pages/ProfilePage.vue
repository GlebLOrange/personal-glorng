<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import ContactLinkChip from "@/components/contact/ContactLinkChip.vue";
import SectionWrapper from "@/components/layout/SectionWrapper.vue";
import EducationList from "@/components/resume/EducationList.vue";
import HeroBlock from "@/components/resume/HeroBlock.vue";
import SkillsGrid from "@/components/resume/SkillsGrid.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import { api } from "@/composables/useApi";
import { buildContactLinks } from "@/constants/contactMeta";
import { RESUME_FALLBACK } from "@/constants/resumeFallback";
import type { ResumeData, ResumeProfileSelection } from "@/types";
import { applyPageSeo } from "@/utils/pageSeo";
import { buildShareProfilePath, parseShareCsv } from "@/utils/resumeShare";

const ExperienceList = defineAsyncComponent(() => import("@/components/resume/ExperienceList.vue"));
const CaseStudies = defineAsyncComponent(() => import("@/components/resume/CaseStudies.vue"));
const FeedbackModal = defineAsyncComponent(() => import("@/components/feedback/FeedbackModal.vue"));

const route = useRoute();
const loading = ref(true);
const apiError = ref(false);
const selection = ref<ResumeProfileSelection | null>(null);
const contactModal = ref<"inquiry" | null>(null);

const resume = computed<ResumeData>(() => selection.value?.resume ?? RESUME_FALLBACK);
const contactLinks = computed(() => buildContactLinks(resume.value.links));
const education = computed(() => resume.value.education ?? []);
const certifications = computed(() => resume.value.certifications ?? []);
const languages = computed(() => resume.value.languages ?? []);
const ignoredNote = computed(() => {
  const ignored = selection.value;
  if (!ignored) return "";
  const parts: string[] = [];
  if (ignored.ignored_skills.length) {
    parts.push(`unknown skills: ${ignored.ignored_skills.join(", ")}`);
  }
  if (ignored.ignored_projects.length) {
    parts.push(`unknown projects: ${ignored.ignored_projects.join(", ")}`);
  }
  if (ignored.ignored_sections.length) {
    parts.push(`unknown sections: ${ignored.ignored_sections.join(", ")}`);
  }
  return parts.join("; ");
});

const showSummary = computed(() => Boolean(resume.value.bio || resume.value.hiring_note));
const showSkills = computed(() => resume.value.skills.length > 0);
const showExperience = computed(() => resume.value.experience.length > 0);
const showProjects = computed(() => resume.value.projects.length > 0);
const showEducation = computed(() => education.value.length > 0);
const showCertifications = computed(() => certifications.value.length > 0);
const showLanguages = computed(() => languages.value.length > 0);
const showLinks = computed(() => contactLinks.value.length > 0);

function sharePathFromRoute(): string {
  return buildShareProfilePath({
    sections: parseShareCsv(route.query.sections),
    skills: parseShareCsv(route.query.skills),
    projects: parseShareCsv(route.query.projects),
  });
}

function applyProfileSeo(data: ResumeData): void {
  const path = sharePathFromRoute();
  const skillLabels = data.skills.flatMap((group) => group.items).slice(0, 4);
  const title =
    skillLabels.length > 0
      ? skillLabels.join(", ")
      : data.projects.length > 0
        ? data.projects
            .slice(0, 2)
            .map((project) => project.name)
            .join(", ")
        : data.title;
  const descriptionParts = [
    data.bio || data.tagline || `${data.name} — ${data.title}`,
  ];
  const allSkills = data.skills.flatMap((group) => group.items).slice(0, 6);
  if (allSkills.length) {
    descriptionParts.push(`Skills: ${allSkills.join(", ")}.`);
  }
  const projectNames = data.projects.map((project) => project.name).slice(0, 3);
  if (projectNames.length) {
    descriptionParts.push(`Projects: ${projectNames.join(", ")}.`);
  }
  applyPageSeo({
    title,
    description: descriptionParts.join(" ").slice(0, 300),
    path,
  });
}

async function loadProfile(): Promise<void> {
  loading.value = true;
  apiError.value = false;
  try {
    const params = new URLSearchParams();
    const sections = parseShareCsv(route.query.sections);
    const skills = parseShareCsv(route.query.skills);
    const projects = parseShareCsv(route.query.projects);
    if (sections.length) params.set("sections", sections.join(","));
    if (skills.length) params.set("skills", skills.join(","));
    if (projects.length) params.set("projects", projects.join(","));
    const query = params.toString();
    const { data } = await api.get<ResumeProfileSelection>(
      `/resume/profile${query ? `?${query}` : ""}`,
    );
    selection.value = data;
    applyProfileSeo(data.resume);
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    apiError.value = true;
    selection.value = {
      resume: RESUME_FALLBACK,
      ignored_skills: [],
      ignored_projects: [],
      ignored_sections: [],
    };
    applyProfileSeo(RESUME_FALLBACK);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void loadProfile();
});

watch(
  () => [route.query.skills, route.query.projects, route.query.sections],
  () => {
    void loadProfile();
  },
);
</script>

<template>
  <div class="portfolio-cv" :aria-busy="loading">
    <div v-if="apiError" class="mx-auto max-w-5xl px-6 pt-4 print:hidden">
      <ErrorState
        message="Using cached portfolio data — live sync unavailable."
        show-retry
        retry-label="retry sync"
        retry-icon="sync"
        @retry="loadProfile"
      />
    </div>

    <div
      v-if="ignoredNote"
      class="mx-auto max-w-5xl px-6 pt-4 print:hidden"
      role="status"
    >
      <p class="text-meta rounded-lg border border-surface-border/60 bg-surface-card/40 px-3 py-2">
        Some share filters were ignored ({{ ignoredNote }}).
      </p>
    </div>

    <SectionWrapper width="full">
      <HeroBlock
        :name="resume.name"
        :title="resume.title"
        :tagline="resume.tagline"
        :location="resume.location"
        :availability="resume.availability"
        @inquire="contactModal = 'inquiry'"
      />
    </SectionWrapper>

    <SectionWrapper v-if="showSummary" id="about" title="about" width="full" dark alternate>
      <p v-if="resume.bio" class="text-body mb-4 max-w-3xl text-pretty">
        {{ resume.bio }}
      </p>
      <p v-if="resume.hiring_note" class="text-body mb-6 max-w-3xl">
        {{ resume.hiring_note }}
      </p>
    </SectionWrapper>

    <SectionWrapper v-if="showExperience" id="experience" title="experience" width="full" dark>
      <Suspense>
        <ExperienceList :experience="resume.experience" />
        <template #fallback>
          <div class="h-40 animate-pulse rounded-lg bg-surface-card" aria-hidden="true" />
        </template>
      </Suspense>
    </SectionWrapper>

    <SectionWrapper
      v-if="showProjects"
      id="case-studies"
      title="case studies"
      width="full"
      dark
      alternate
    >
      <Suspense>
        <CaseStudies :projects="resume.projects" />
        <template #fallback>
          <div class="h-40 animate-pulse rounded-lg bg-surface-card" aria-hidden="true" />
        </template>
      </Suspense>
    </SectionWrapper>

    <SectionWrapper v-if="showSkills" id="skills" title="skills" width="full" dark>
      <SkillsGrid :skills="resume.skills" />
    </SectionWrapper>

    <SectionWrapper
      v-if="showEducation"
      id="education"
      title="education"
      width="prose"
      dark
      alternate
    >
      <EducationList :education="education" />
    </SectionWrapper>

    <SectionWrapper
      v-if="showCertifications"
      id="certifications"
      title="certifications"
      width="prose"
      dark
    >
      <ul class="m-0 list-none space-y-3 p-0">
        <li v-for="item in certifications" :key="item.name" class="text-body">
          <span class="font-medium text-surface-light">{{ item.name }}</span>
          <span v-if="item.issuer" class="text-meta"> — {{ item.issuer }}</span>
          <span v-if="item.period" class="text-meta"> ({{ item.period }})</span>
        </li>
      </ul>
    </SectionWrapper>

    <SectionWrapper v-if="showLanguages" id="languages" title="languages" width="prose" dark>
      <ul class="m-0 list-none space-y-2 p-0">
        <li v-for="item in languages" :key="item.language" class="text-body">
          {{ item.language
          }}<span v-if="item.proficiency" class="text-meta"> — {{ item.proficiency }}</span>
        </li>
      </ul>
    </SectionWrapper>

    <SectionWrapper v-if="showLinks" id="contacts" title="contacts" width="full" dark>
      <div class="flex flex-wrap gap-4">
        <ContactLinkChip v-for="link in contactLinks" :key="link.id" :link="link" />
      </div>
      <FeedbackModal v-if="contactModal" :intent="contactModal" @close="contactModal = null" />
    </SectionWrapper>
  </div>
</template>
