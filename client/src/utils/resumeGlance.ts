import type { Experience, ResumeData, SkillGroup } from "@/types";

export interface GlanceStat {
  label: string;
  value: string;
  detail: string;
}

function parsePeriodStart(period: string): number | null {
  const match = period.match(/^(\d{4})/);
  return match ? Number.parseInt(match[1], 10) : null;
}

function parsePeriodEnd(period: string): number {
  if (/present/i.test(period)) {
    return new Date().getFullYear();
  }
  const match = period.match(/-\s*(\d{4})/);
  return match ? Number.parseInt(match[1], 10) : new Date().getFullYear();
}

export function computeYearsExperience(experience: Experience[]): number {
  if (experience.length === 0) {
    return 0;
  }

  const starts = experience
    .map((entry) => parsePeriodStart(entry.period))
    .filter((year): year is number => year !== null);
  const ends = experience.map((entry) => parsePeriodEnd(entry.period));

  if (starts.length === 0) {
    return 0;
  }

  const earliest = Math.min(...starts);
  const latest = Math.max(...ends);
  return Math.max(1, latest - earliest + 1);
}

export function countSkills(skills: SkillGroup[]): number {
  return skills.reduce((total, group) => total + group.items.length, 0);
}

export function primaryStack(skills: SkillGroup[]): string {
  const backend = skills.find((group) => group.category === "Backend")?.items ?? [];
  const frontend = skills.find((group) => group.category === "Frontend")?.items ?? [];
  const picks = [backend[0], frontend[0], backend[2]].filter(Boolean);
  return picks.length > 0 ? picks.join(" · ") : "Full-stack";
}

export function buildGlanceStats(resume: ResumeData): GlanceStat[] {
  const years = computeYearsExperience(resume.experience);
  const skillCount = countSkills(resume.skills);

  return [
    {
      label: "Experience",
      value: years > 0 ? `${years}+ yrs` : "—",
      detail: years > 0 ? "Building and shipping products" : "No entries yet",
    },
    {
      label: "Core stack",
      value: primaryStack(resume.skills),
      detail: `${skillCount} tools across ${resume.skills.length} areas`,
    },
    {
      label: "Projects",
      value: String(resume.projects.length),
      detail: "Highlighted work with live links",
    },
    {
      label: "Availability",
      value: resume.availability ? "Open" : "—",
      detail: resume.availability ?? resume.location ?? "Add availability in resume data",
    },
  ];
}
