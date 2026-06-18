import axios, { AxiosError } from "axios";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "@/composables/useApi";
import { useCachedApi } from "@/composables/useCachedApi";
import { useAuthStore } from "@/stores/auth";

const { signInWithGooglePopupMock } = vi.hoisted(() => ({
  signInWithGooglePopupMock: vi.fn(),
}));

vi.mock("@/composables/useApi", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

vi.mock("@/services/firebase", () => ({
  signInWithGooglePopup: signInWithGooglePopupMock,
}));

describe("useAuthStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it("clearUser clears cached API responses", async () => {
    vi.mocked(api.get).mockResolvedValue({ data: { ok: true } });

    const cached = useCachedApi<{ ok: boolean }>("/auth-cache-test", 60_000);
    await cached.fetch();
    expect(api.get).toHaveBeenCalledTimes(1);

    const auth = useAuthStore();
    auth.clearUser();

    const again = useCachedApi<{ ok: boolean }>("/auth-cache-test", 60_000);
    await again.fetch();
    expect(api.get).toHaveBeenCalledTimes(2);
  });

  it("clears user on clearUser", () => {
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
    auth.clearUser();
    expect(auth.user).toBeNull();
    expect(auth.isAuthenticated).toBe(false);
  });

  it("login fetches user after credentials post", async () => {
    vi.mocked(api.post).mockResolvedValue({ data: {} });
    vi.mocked(api.get).mockResolvedValue({
      data: {
        id: "u1",
        email: "admin@admin.admin",
        permissions: ["*"],
        is_verified: true,
        display_name: "Admin",
        timezone: "UTC",
        preferences: {},
        created_at: "2026-01-01T00:00:00Z",
      },
    });

    const auth = useAuthStore();
    await auth.login("admin@admin.admin", "MyTestPass123!");

    expect(api.post).toHaveBeenCalledWith("/auth/login", {
      email: "admin@admin.admin",
      password: "MyTestPass123!",
    });
    expect(auth.user?.email).toBe("admin@admin.admin");
    expect(auth.isAuthenticated).toBe(true);
  });

  it("exchanges Google Firebase token then fetches user", async () => {
    const getIdToken = vi.fn().mockResolvedValue("firebase-token");
    signInWithGooglePopupMock.mockResolvedValue({ user: { getIdToken } });
    vi.mocked(api.post).mockResolvedValue({ data: {} });
    vi.mocked(api.get).mockResolvedValue({
      data: {
        id: "u1",
        email: "google@example.com",
        permissions: [],
        is_verified: true,
        display_name: "Google User",
        timezone: "UTC",
        preferences: {},
        created_at: "2026-01-01T00:00:00Z",
      },
    });

    const auth = useAuthStore();
    await auth.loginWithGoogle();

    expect(api.post).toHaveBeenCalledWith("/auth/firebase", {
      id_token: "firebase-token",
    });
    expect(auth.user?.email).toBe("google@example.com");
  });

  it("resolveSession clears user on 401 after refresh fails", async () => {
    const err401 = new AxiosError("Unauthorized");
    err401.response = { status: 401 } as NonNullable<AxiosError["response"]>;
    vi.mocked(api.get).mockRejectedValue(err401);
    vi.mocked(api.post).mockRejectedValue(err401);
    vi.spyOn(axios, "isAxiosError").mockReturnValue(true);

    const auth = useAuthStore();
    await auth.resolveSession();

    expect(auth.user).toBeNull();
    expect(auth.sessionResolved).toBe(true);
  });
});
