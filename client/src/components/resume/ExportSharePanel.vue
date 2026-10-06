<script setup lang="ts">
import { computed, ref } from "vue";

import { useClipboard } from "@/composables/useClipboard";
import { useNotify } from "@/composables/useNotify";
import type { ResumeData, ResumeSectionId } from "@/types";
import {
  downloadResumeExport,
  resumeDownloadErrorMessage,
  type ResumeDownloadKind,
} from "@/utils/resumeDownload";
import { buildShareProfilePath, skillId } from "@/utils/resumeShare";

const props = defineProps<{
  resume: ResumeData;
}>();

const SECTION_OPTIONS: { id: ResumeSectionId; label: string }[] = [
  { id: "summary", label: "summary" },
  { id: "skills", label: "skills" },
  { id: "experience", label: "experience" },
  { id: "projects", label: "projects" },
  { id: "education", label: "education" },
  { id: "certifications", label: "certifications" },
  { id: "languages", label: "languages" },
  { id: "links", label: "links" },
];

const { toast } = useNotify();
const { copy } = useClipboard();

const downloading = ref<ResumeDownloadKind | null>(null);
const copyingRecruiter = ref(false);
const showShare = ref(false);
const selectedSkills = ref<string[]>([]);
const selectedProjects = ref<string[]>([]);
const selectedSections = ref<ResumeSectionId[]>([]);

const skillOptions = computed(() => {
  const seen = new Set<string>();
  const options: { id: string; label: string }[] = [];
  for (const group of props.resume.skills) {
    for (const item of group.items) {
      const id = skillId(item);
      if (!id || seen.has(id)) continue;
      seen.add(id);
      options.push({ id, label: item });
    }
  }
  return options;
});

const projectOptions = computed(() =>
  props.resume.projects.map((project) => ({
    id: project.slug,
    label: project.name,
  })),
);

const sharePath = computed(() =>
  buildShareProfilePath({
    sections: selectedSections.value,
    skills: selectedSkills.value,
    projects: selectedProjects.value,
  }),
);

const shareUrl = computed(() => {
  if (typeof window === "undefined") return sharePath.value;
  return `${window.location.origin}${sharePath.value}`;
});

async function handleDownload(kind: ResumeDownloadKind): Promise<void> {
  if (downloading.value) return;
  downloading.value = kind;
  try {
    await downloadResumeExport(kind);
    toast(`${kind === "pdf" ? "PDF" : kind === "markdown" ? "Markdown" : "JSON"} downloaded`, "success");
  } catch (err) {
    toast(await resumeDownloadErrorMessage(err, `Failed to download ${kind}`), "error");
  } finally {
    downloading.value = null;
  }
}

async function copyRecruiterProfile(): Promise<void> {
  if (copyingRecruiter.value) return;
  copyingRecruiter.value = true;
  try {
    const { api } = await import("@/composables/useApi");
    const { data } = await api.get<string>("/resume/recruiter-profile", {
      responseType: "text",
      headers: { Accept: "text/plain" },
    });
    await copy(String(data).trim());
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to copy recruiter profile", "error");
  } finally {
    copyingRecruiter.value = false;
  }
}

async function copyShareUrl(): Promise<void> {
  await copy(shareUrl.value);
}

function toggleSkill(id: string): void {
  const set = new Set(selectedSkills.value);
  if (set.has(id)) set.delete(id);
  else set.add(id);
  selectedSkills.value = [...set];
}

function toggleProject(id: string): void {
  const set = new Set(selectedProjects.value);
  if (set.has(id)) set.delete(id);
  else set.add(id);
  selectedProjects.value = [...set];
}

function toggleSection(id: ResumeSectionId): void {
  const set = new Set(selectedSections.value);
  if (set.has(id)) set.delete(id);
  else set.add(id);
  selectedSections.value = [...set];
}
</script>

<template>
  <div class="print:hidden space-y-6">
    <div class="flex flex-col sm:flex-row flex-wrap gap-2">
      <button
        type="button"
        class="cta-secondary"
        :disabled="downloading !== null"
        @click="handleDownload('pdf')"
      >
        {{ downloading === "pdf" ? "downloading…" : "Download PDF" }}
      </button>
      <button
        type="button"
        class="cta-secondary"
        :disabled="downloading !== null"
        @click="handleDownload('markdown')"
      >
        {{ downloading === "markdown" ? "downloading…" : "Export Markdown" }}
      </button>
      <button
        type="button"
        class="cta-secondary"
        :disabled="downloading !== null"
        @click="handleDownload('json')"
      >
        {{ downloading === "json" ? "downloading…" : "Export JSON" }}
      </button>
    </div>

    <div class="flex flex-col sm:flex-row flex-wrap gap-2">
      <button
        type="button"
        class="cta-secondary"
        :disabled="copyingRecruiter"
        @click="copyRecruiterProfile"
      >
        {{ copyingRecruiter ? "copying…" : "Copy Recruiter Profile" }}
      </button>
      <button type="button" class="cta-secondary" @click="showShare = !showShare">
        {{ showShare ? "Hide Share Profile" : "Share Profile" }}
      </button>
    </div>

    <div
      v-if="showShare"
      class="rounded-lg border border-surface-border/60 bg-surface-card/30 p-4 space-y-4"
    >
      <fieldset>
        <legend class="text-meta mb-2">Sections</legend>
        <div class="flex flex-wrap gap-2">
          <label
            v-for="option in SECTION_OPTIONS"
            :key="option.id"
            class="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-lg border border-surface-border/50 px-3 text-sm"
          >
            <input
              type="checkbox"
              class="size-4 accent-accent-blue"
              :checked="selectedSections.includes(option.id)"
              @change="toggleSection(option.id)"
            />
            {{ option.label }}
          </label>
        </div>
      </fieldset>

      <fieldset>
        <legend class="text-meta mb-2">Skills</legend>
        <div class="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
          <label
            v-for="option in skillOptions"
            :key="option.id"
            class="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-lg border border-surface-border/50 px-3 text-sm"
          >
            <input
              type="checkbox"
              class="size-4 accent-accent-blue"
              :checked="selectedSkills.includes(option.id)"
              @change="toggleSkill(option.id)"
            />
            {{ option.label }}
          </label>
        </div>
      </fieldset>

      <fieldset>
        <legend class="text-meta mb-2">Projects</legend>
        <div class="flex flex-wrap gap-2">
          <label
            v-for="option in projectOptions"
            :key="option.id"
            class="inline-flex min-h-11 cursor-pointer items-center gap-2 rounded-lg border border-surface-border/50 px-3 text-sm"
          >
            <input
              type="checkbox"
              class="size-4 accent-accent-blue"
              :checked="selectedProjects.includes(option.id)"
              @change="toggleProject(option.id)"
            />
            {{ option.label }}
          </label>
        </div>
      </fieldset>

      <div class="space-y-2">
        <p class="text-meta">Share URL</p>
        <code
          class="block break-all rounded-lg border border-surface-border/50 bg-surface-dark/60 px-3 py-2 text-sm text-surface-light"
        >
          {{ shareUrl }}
        </code>
        <button type="button" class="cta-primary" @click="copyShareUrl">Copy URL</button>
      </div>
    </div>
  </div>
</template>
