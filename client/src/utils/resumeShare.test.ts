import { flushPromises, mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ProfilePage from "@/pages/ProfilePage.vue";
import { RESUME_FALLBACK } from "@/constants/resumeFallback";
import type { ResumeProfileSelection } from "@/types";
import { buildShareProfilePath, skillId } from "@/utils/resumeShare";

const apiGet = vi.fn();

vi.mock("@/composables/useApi", () => ({
  api: {
    get: (...args: unknown[]) => apiGet(...args),
  },
}));

vi.mock("@/utils/pageSeo", () => ({
  applyPageSeo: vi.fn(),
}));

describe("resumeShare", () => {
  it("derives skill ids", () => {
    expect(skillId("Python")).toBe("python");
    expect(skillId("Vue 3")).toBe("vue-3");
    expect(skillId("CI/CD (GitHub Actions)")).toBe("ci-cd");
  });

  it("builds deterministic share paths", () => {
    expect(
      buildShareProfilePath({
        projects: ["ssrf-safe-fetch", "cookie-auth-csrf"],
        skills: ["fastapi", "python"],
        sections: ["projects", "skills"],
      }),
    ).toBe(
      "/profile?sections=projects,skills&skills=fastapi,python&projects=cookie-auth-csrf,ssrf-safe-fetch",
    );
    expect(buildShareProfilePath({})).toBe("/profile");
  });
});

describe("ProfilePage", () => {
  beforeEach(() => {
    apiGet.mockReset();
  });

  it("renders a filtered profile from the API and notes ignored ids", async () => {
    const filtered: ResumeProfileSelection = {
      resume: {
        ...RESUME_FALLBACK,
        skills: [{ category: "Backend", items: ["Python", "FastAPI"] }],
        projects: [RESUME_FALLBACK.projects[0]!],
        experience: [],
        education: [],
        certifications: [],
        languages: [],
        links: { github: RESUME_FALLBACK.links.github },
      },
      ignored_skills: ["nope"],
      ignored_projects: [],
      ignored_sections: [],
    };
    apiGet.mockResolvedValue({ data: filtered });

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: "/profile", name: "profile", component: ProfilePage }],
    });
    await router.push("/profile?skills=python,fastapi,nope&projects=cookie-auth-csrf");
    await router.isReady();

    const wrapper = mount(ProfilePage, {
      global: {
        plugins: [router],
        stubs: {
          ExperienceList: true,
          CaseStudies: {
            props: ["projects"],
            template: "<div class='cases'>{{ projects.map(p => p.name).join(', ') }}</div>",
          },
          FeedbackModal: true,
          HeroBlock: {
            template: "<div class='hero'>{{ name }}</div>",
            props: ["name", "title", "tagline", "location", "availability"],
          },
        },
      },
    });

    await flushPromises();

    expect(apiGet).toHaveBeenCalled();
    expect(wrapper.text()).toContain("Gleb.Y");
    expect(wrapper.text()).toContain("Python");
    expect(wrapper.text()).toContain("FastAPI");
    expect(wrapper.text()).toContain("cookie auth & CSRF");
    expect(wrapper.text()).toContain("unknown skills: nope");
  });

  it("falls back to the full profile when the query is empty", async () => {
    const full: ResumeProfileSelection = {
      resume: RESUME_FALLBACK,
      ignored_skills: [],
      ignored_projects: [],
      ignored_sections: [],
    };
    apiGet.mockResolvedValue({ data: full });

    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: "/profile", name: "profile", component: ProfilePage }],
    });
    await router.push("/profile");
    await router.isReady();

    const wrapper = mount(ProfilePage, {
      global: {
        plugins: [router],
        stubs: {
          ExperienceList: {
            props: ["experience"],
            template: "<div class='exp'>{{ experience.length }} roles</div>",
          },
          CaseStudies: true,
          FeedbackModal: true,
          HeroBlock: {
            template: "<div class='hero'>{{ name }}</div>",
            props: ["name", "title", "tagline", "location", "availability"],
          },
        },
      },
    });

    await flushPromises();

    expect(wrapper.text()).toContain(`${RESUME_FALLBACK.experience.length} roles`);
    expect(wrapper.text()).toContain("Backend");
  });
});
