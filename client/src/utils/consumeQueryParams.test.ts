import { describe, expect, it, vi } from "vitest";
import type { LocationQuery, Router } from "vue-router";

import { consumeQueryParams, omitQueryKeys } from "@/utils/consumeQueryParams";

function mockRouter(replace = vi.fn()): Router {
  return { replace } as unknown as Router;
}

describe("omitQueryKeys", () => {
  it("copies query without the listed keys", () => {
    const query: LocationQuery = { token: "secret", next: "/admin", empty: null };
    expect(omitQueryKeys(query, ["token"])).toEqual({ next: "/admin", empty: null });
    expect(query).toEqual({ token: "secret", next: "/admin", empty: null });
  });
});

describe("consumeQueryParams", () => {
  it("strips keys via replace and returns string values", async () => {
    const replace = vi.fn().mockResolvedValue(undefined);
    const router = mockRouter(replace);
    const query: LocationQuery = {
      token: "abc",
      code: "xyz",
      keep: "yes",
    };

    const values = await consumeQueryParams(router, "/callback", query, ["token", "code"]);

    expect(values).toEqual({ token: "abc", code: "xyz" });
    expect(replace).toHaveBeenCalledWith({
      path: "/callback",
      query: { keep: "yes" },
    });
  });

  it("preserves other query keys when stripping", async () => {
    const replace = vi.fn().mockResolvedValue(undefined);
    const router = mockRouter(replace);
    const query: LocationQuery = { token: "t", next: "/settings", tab: "profile" };

    await consumeQueryParams(router, "/verify-email", query, ["token"]);

    expect(replace).toHaveBeenCalledWith({
      path: "/verify-email",
      query: { next: "/settings", tab: "profile" },
    });
  });

  it("maps non-string and array values to undefined", async () => {
    const replace = vi.fn().mockResolvedValue(undefined);
    const router = mockRouter(replace);
    const query: LocationQuery = {
      token: ["a", "b"],
      code: null,
    };

    const values = await consumeQueryParams(router, "/callback", query, ["token", "code"]);

    expect(values).toEqual({ token: undefined, code: undefined });
    expect(replace).toHaveBeenCalledOnce();
  });

  it("is a no-op when keys are absent", async () => {
    const replace = vi.fn().mockResolvedValue(undefined);
    const router = mockRouter(replace);
    const query: LocationQuery = { next: "/home" };

    const values = await consumeQueryParams(router, "/reset-password", query, ["token"]);

    expect(values).toEqual({ token: undefined });
    expect(replace).not.toHaveBeenCalled();
  });
});
