import type { Experience, ResumeData, SkillGroup } from "@/types";

export interface GlanceStat {
  label: string;
  value: string;
  detail: string;
  href: string;
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
  // Prefer FastAPI (backend[1]) over later libs for hiring glance signal
  const picks = [backend[0], frontend[0], backend[1]].filter(Boolean);
  return picks.length > 0 ? picks.join(" · ") : "Full-stack";
}

/** Hiring-relevant glance only — years and shipped systems, not vanity cards. */
export function buildGlanceStats(resume: ResumeData): GlanceStat[] {
  const years = computeYearsExperience(resume.experience);
  const shipped = resume.projects.filter((project) => Boolean(project.result)).length;
  const stats: GlanceStat[] = [];

  if (years > 0) {
    stats.push({
      label: "Experience",
      value: `${years}+`,
      detail: "years across production backend roles",
      href: "#experience",
    });
  }

  if (shipped > 0) {
    stats.push({
      label: "Case studies",
      value: String(shipped),
      detail: "production systems with written outcomes",
      href: "#case-studies",
    });
  }

  if (resume.availability) {
    stats.push({
      label: "Availability",
      value: "open",
      detail: resume.availability,
      href: "#contacts",
    });
  }

  return stats;
}
