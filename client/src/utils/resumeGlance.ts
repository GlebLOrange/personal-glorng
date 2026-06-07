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

export function topSkillCategories(skills: SkillGroup[], limit = 3): string {
  return skills
    .slice(0, limit)
    .map((group) => group.category)
    .join(", ");
}

export function buildGlanceStats(resume: ResumeData): GlanceStat[] {
  const years = computeYearsExperience(resume.experience);
  const skillCount = countSkills(resume.skills);

  return [
    {
      label: "Experience",
      value: years > 0 ? `${years}+` : "—",
      detail: years > 0 ? "Years building products" : "No entries yet",
    },
    {
      label: "Skills",
      value: String(skillCount),
      detail: topSkillCategories(resume.skills) || "Skill groups",
    },
    {
      label: "Projects",
      value: String(resume.projects.length),
      detail: "Highlighted work",
    },
    {
      label: "Focus",
      value: String(resume.skills.length),
      detail: "Skill areas covered",
    },
  ];
}
