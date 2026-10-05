/**
 * @vitest-environment jsdom
 */
import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import PrivacyPage from "@/pages/PrivacyPage.vue";

const showPreferences = vi.fn();

vi.mock("vanilla-cookieconsent", () => ({
  showPreferences: (...args: unknown[]) => showPreferences(...args),
}));

vi.mock("@/constants/firebase", () => ({
  isFirebaseAnalyticsEnabled: false,
}));

vi.mock("@/constants/sentry", () => ({
  isSentryEnabled: false,
}));

const pageShellStub = {
  props: ["title", "breadcrumbs", "backTo", "maxWidth"],
  template: '<div data-testid="shell"><h1>{{ title }}</h1><slot /></div>',
};

describe("PrivacyPage", () => {
  it("shows policy sections and opens cookie preferences", async () => {
    showPreferences.mockClear();
    const wrapper = mount(PrivacyPage, {
      global: {
        stubs: {
          PageShell: pageShellStub,
          ContactLinkChip: true,
        },
      },
    });

    expect(wrapper.get("h1").text()).toBe("Privacy policy");
    expect(wrapper.text()).toContain("What data is collected");
    expect(wrapper.text()).toContain("Cookies used");
    expect(wrapper.text()).toContain("cc_cookie");
    expect(wrapper.text()).toContain(
      "Optional analytics and error monitoring are currently disabled.",
    );
    expect(wrapper.text()).not.toContain("Firebase Analytics");

    await wrapper.get('button[type="button"]').trigger("click");
    expect(showPreferences).toHaveBeenCalledTimes(1);
  });
});
