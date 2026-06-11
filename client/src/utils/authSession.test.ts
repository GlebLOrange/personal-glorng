import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "@/composables/useApi";
import { useAuthStore } from "@/stores/auth";
import { handleAuthFailure, tryRefreshSession } from "@/utils/authSession";

vi.mock("@/composables/useApi", () => ({
  api: {
    post: vi.fn(),
  },
}));

vi.mock("@/router", () => ({
  default: {
    currentRoute: { value: { path: "/admin", meta: { requiresAuth: true }, fullPath: "/admin" } },
    replace: vi.fn(),
  },
}));

describe("authSession", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it("tryRefreshSession returns true on success", async () => {
    vi.mocked(api.post).mockResolvedValue({ data: {} });

    const result = await tryRefreshSession();

    expect(result).toBe(true);
    expect(api.post).toHaveBeenCalledWith("/auth/refresh");
  });

  it("tryRefreshSession clears user on failure", async () => {
    vi.mocked(api.post).mockRejectedValue(new Error("refresh failed"));

    const auth = useAuthStore();
    auth.user = {
      id: "1",
      email: "a@b.c",
      permissions: [],
      is_verified: true,
      display_name: "User",
      timezone: "UTC",
      preferences: {},
      created_at: "2026-01-01T00:00:00Z",
    };

    const result = await tryRefreshSession();

    expect(result).toBe(false);
    expect(auth.user).toBeNull();
  });

  it("handleAuthFailure redirects protected routes to login", async () => {
    const router = (await import("@/router")).default;

    await handleAuthFailure();

    expect(router.replace).toHaveBeenCalledWith({
      path: "/login",
      query: { redirect: "/admin" },
    });
  });
});
