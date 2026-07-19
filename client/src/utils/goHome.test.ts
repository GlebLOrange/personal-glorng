import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Router } from "vue-router";

import { goHome } from "./goHome";

function mockRouter(path: string, hash = ""): Router {
  return {
    currentRoute: { value: { path, hash } },
    push: vi.fn().mockResolvedValue(undefined),
    replace: vi.fn().mockResolvedValue(undefined),
  } as unknown as Router;
}

describe("goHome", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "matchMedia",
      vi.fn().mockReturnValue({ matches: true, addEventListener: vi.fn(), removeEventListener: vi.fn() }),
    );
    vi.spyOn(window, "scrollTo").mockImplementation(() => undefined);
  });

  it("pushes / when on another route", async () => {
    const router = mockRouter("/news");
    await goHome(router);
    expect(router.push).toHaveBeenCalledWith("/");
    expect(window.scrollTo).not.toHaveBeenCalled();
  });

  it("scrolls to top when already on /", async () => {
    const router = mockRouter("/");
    await goHome(router);
    expect(router.push).not.toHaveBeenCalled();
    expect(router.replace).not.toHaveBeenCalled();
    expect(window.scrollTo).toHaveBeenCalledWith({ top: 0, behavior: "instant" });
  });

  it("clears hash then scrolls when on /#section", async () => {
    const router = mockRouter("/", "#projects");
    await goHome(router);
    expect(router.replace).toHaveBeenCalledWith({ path: "/" });
    expect(window.scrollTo).toHaveBeenCalledWith({ top: 0, behavior: "instant" });
  });
});
