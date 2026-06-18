import type { App } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  acceptedCategory: vi.fn(),
  initFirebaseAnalytics: vi.fn(),
  initSentry: vi.fn(),
  run: vi.fn(),
  router: { afterEach: vi.fn() },
}));

vi.mock("vanilla-cookieconsent", () => ({
  acceptedCategory: mocks.acceptedCategory,
  run: mocks.run,
}));

vi.mock("vanilla-cookieconsent/dist/cookieconsent.css", () => ({}));

vi.mock("@/constants/firebase", () => ({
  isFirebaseAnalyticsEnabled: true,
}));

vi.mock("@/constants/sentry", () => ({
  isSentryEnabled: false,
}));

vi.mock("@/instrument", () => ({
  initSentry: mocks.initSentry,
}));

vi.mock("@/services/firebase", () => ({
  initFirebaseAnalytics: mocks.initFirebaseAnalytics,
}));

vi.mock("@/router", () => ({
  default: mocks.router,
}));

describe("setupCookieConsent", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("initializes Firebase Analytics only after analytics consent", async () => {
    const { setupCookieConsent } = await import("@/composables/useCookieConsent");
    const app = {} as App;

    mocks.acceptedCategory.mockReturnValue(false);
    setupCookieConsent(app);

    const config = mocks.run.mock.calls[0]?.[0];
    expect(config).toBeTruthy();
    config.onConsent();
    expect(mocks.initFirebaseAnalytics).not.toHaveBeenCalled();

    mocks.acceptedCategory.mockImplementation((category: string) => category === "analytics");
    config.onChange();

    expect(mocks.initFirebaseAnalytics).toHaveBeenCalledOnce();
    expect(mocks.initFirebaseAnalytics).toHaveBeenCalledWith(mocks.router);
  });
});
