import { describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  app: {
    component: vi.fn(),
    mount: vi.fn(),
    use: vi.fn(),
  },
  router: {
    isReady: vi.fn(() => Promise.resolve()),
  },
  restoreAuth: vi.fn(),
}));

vi.mock("vue", async (importActual) => {
  const actual = await importActual<typeof import("vue")>();
  return {
    ...actual,
    createApp: vi.fn(() => mocks.app),
  };
});

vi.mock("@/plugins/auth", () => ({
  restoreAuth: mocks.restoreAuth,
}));

vi.mock("./router", () => ({
  default: mocks.router,
}));

describe("main", () => {
  it("starts auth restoration after mounting the app", async () => {
    await import("@/main");
    await mocks.router.isReady.mock.results[0]?.value;

    expect(mocks.app.mount).toHaveBeenCalledWith("#app");
    expect(mocks.restoreAuth).toHaveBeenCalledOnce();
  });
});
