"""Canonical resume document schema — single source of truth for exports."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ResumeSectionId = Literal[
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
    "languages",
    "links",
]

RESUME_SECTION_IDS: tuple[ResumeSectionId, ...] = (
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
    "languages",
    "links",
)


class ResumeSkillGroup(BaseModel):
    """Grouped skill list with optional category summary."""

    category: str = Field(min_length=1)
    items: list[str] = Field(min_length=1)
    summary: str | None = None


class ResumeExperience(BaseModel):
    """One work-history entry."""

    role: str = Field(min_length=1)
    company: str = Field(min_length=1)
    period: str = Field(min_length=1)
    description: str = Field(min_length=1)
    highlights: list[str] = Field(default_factory=list)


class ResumeEducation(BaseModel):
    """One education entry."""

    degree: str = Field(min_length=1)
    institution: str = Field(min_length=1)
    period: str = Field(min_length=1)
    description: str | None = None


class ResumeProject(BaseModel):
    """Case study / project with a stable slug for share URLs."""

    slug: str = Field(min_length=1, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    tech: list[str] = Field(default_factory=list)
    url: str = ""
    problem: str | None = None
    approach: str | None = None
    result: str | None = None


class ResumeCertification(BaseModel):
    """Optional certification entry."""

    name: str = Field(min_length=1)
    issuer: str | None = None
    period: str | None = None
    url: str | None = None


class ResumeLanguage(BaseModel):
    """Spoken / written language proficiency."""

    language: str = Field(min_length=1)
    proficiency: str | None = None


class ResumeLinks(BaseModel):
    """Contact and profile links."""

    model_config = ConfigDict(extra="forbid")

    email: str | None = None
    telegram: str | None = None
    linkedin: str | None = None
    github: str | None = None


class ResumeDocument(BaseModel):
    """Canonical CV payload used by the site and every export."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    title: str = Field(min_length=1)
    tagline: str | None = None
    location: str | None = None
    availability: str | None = None
    # bio/skills/experience may be empty on filtered share payloads; the
    # import-time RESUME_DOCUMENT assert keeps the canonical CV complete.
    bio: str = ""
    hiring_note: str | None = None
    skills: list[ResumeSkillGroup] = Field(default_factory=list)
    experience: list[ResumeExperience] = Field(default_factory=list)
    projects: list[ResumeProject] = Field(default_factory=list)
    education: list[ResumeEducation] = Field(default_factory=list)
    certifications: list[ResumeCertification] = Field(default_factory=list)
    languages: list[ResumeLanguage] = Field(default_factory=list)
    links: ResumeLinks


class ResumeProfileSelection(BaseModel):
    """Filtered resume plus ids that did not match the canonical document."""

    resume: ResumeDocument
    ignored_skills: list[str] = Field(default_factory=list)
    ignored_projects: list[str] = Field(default_factory=list)
    ignored_sections: list[str] = Field(default_factory=list)
