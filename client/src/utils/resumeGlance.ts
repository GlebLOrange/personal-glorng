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

/** Short glance value for a case study — prefer an explicit result line. */
function caseOutcomeValue(name: string): string {
  const lower = name.toLowerCase();
  if (lower.includes("csrf") || lower.includes("auth")) return "CSRF";
  if (lower.includes("ssrf") || lower.includes("fetch")) return "SSRF-safe";
  return "shipped";
}

export function buildGlanceStats(resume: ResumeData): GlanceStat[] {
  const cases = resume.projects.filter((project) => project.result).slice(0, 2);
  const platformStart = resume.experience
    .map((entry) => parsePeriodStart(entry.period))
    .filter((year): year is number => year !== null)
    .filter((year) => year >= 2022);
  const since = platformStart.length > 0 ? Math.min(...platformStart) : 2022;

  const outcomeStats: GlanceStat[] = cases.map((project) => ({
    label: project.name,
    value: caseOutcomeValue(project.name),
    detail: project.result ?? project.description,
    href: "#case-studies",
  }));

  while (outcomeStats.length < 2) {
    outcomeStats.push({
      label: "Case study",
      value: "—",
      detail: "add problem / approach / result on a project",
      href: "#case-studies",
    });
  }

  return [
    ...outcomeStats,
    {
      label: "Platform sample",
      value: `since ${since}`,
      detail: "this site is the live FastAPI + Vue product",
      href: "#experience",
    },
    {
      label: "Availability",
      value: resume.availability ? "open" : "—",
      detail: resume.availability ?? resume.location ?? "add availability in resume data",
      href: "#contacts",
    },
  ];
}
