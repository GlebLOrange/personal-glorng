import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "@/composables/useApi";
import {
  clearPlatformCatalog,
  mapApiPlatformService,
  usePlatformCatalog,
} from "@/composables/usePlatformCatalog";
import { useAuthStore } from "@/stores/auth";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";
import type { UserResponse } from "@/types";

vi.mock("@/composables/useApi", () => ({
  api: {
    get: vi.fn(),
  },
}));

vi.mock("@/utils/featureFlags", () => ({
  isAiChatEnabled: vi.fn(() => true),
  isExpensesEnabled: vi.fn(() => true),
}));

import { isAiChatEnabled } from "@/utils/featureFlags";

const base = {
  slug: "tasks",
  name: "tasks",
  category: "productivity",
  category_label: "productivity",
  description: "Manage tasks",
  api_prefix: "/tasks",
  icon: "☐",
  capabilities: ["read"],
  external: false,
};

const catalogPayload = {
  services: [
    {
      ...base,
      admin_route: "/tasks",
    },
    {
      slug: "ai-chat",
      name: "ai chat",
      category: "utilities",
      category_label: "utilities",
      description: "Chat",
      api_prefix: "/ai-chat",
      admin_route: "/admin/ai-chat",
      icon: "⊛",
      capabilities: ["read", "write"],
      external: false,
    },
  ],
};

function makeUser(permissions: string[]): UserResponse {
  return {
    id: "1",
    email: "a@b.c",
    permissions,
    is_verified: true,
    display_name: "User",
    timezone: "UTC",
    preferences: {},
    created_at: "2026-01-01T00:00:00Z",
  };
}

describe("mapApiPlatformService", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("keeps relative admin routes", () => {
    const mapped = mapApiPlatformService({ ...base, admin_route: "/tasks" });
    expect(mapped?.adminRoute).toBe("/tasks");
  });

  it("keeps https external admin routes", () => {
    const mapped = mapApiPlatformService({
      ...base,
      slug: "docs",
      admin_route: "https://example.com/docs",
      external: true,
    });
    expect(mapped?.adminRoute).toBe("https://example.com/docs");
  });

  it("drops services with javascript admin routes", () => {
    expect(mapApiPlatformService({ ...base, admin_route: "javascript:alert(1)" })).toBeNull();
  });

  it("drops services with protocol-relative admin routes", () => {
    expect(mapApiPlatformService({ ...base, admin_route: "//evil.example/x" })).toBeNull();
  });

  it("clears unsafe public_route without dropping the service", () => {
    const mapped = mapApiPlatformService({
      ...base,
      admin_route: "/expenses",
      public_route: "javascript:alert(1)",
    });
    expect(mapped?.adminRoute).toBe("/expenses");
    expect(mapped?.publicRoute).toBeUndefined();
  });

  it("keeps safe public_route", () => {
    const mapped = mapApiPlatformService({
      ...base,
      admin_route: "/expenses",
      public_route: "/expense-calculator",
    });
    expect(mapped?.publicRoute).toBe("/expense-calculator");
  });
});

describe("usePlatformCatalog cache", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    vi.mocked(isAiChatEnabled).mockReturnValue(true);
    clearPlatformCatalog();
  });

  it("hides ai-chat for non-superuser but restores it after superuser login", async () => {
    vi.mocked(api.get).mockResolvedValue({ data: catalogPayload });

    const auth = useAuthStore();
    auth.user = makeUser(["tasks:read"]);

    const catalog = usePlatformCatalog();
    await catalog.load();

    expect(catalog.services.value.some((s) => s.slug === "ai-chat")).toBe(false);
    expect(catalog.services.value.some((s) => s.slug === "tasks")).toBe(true);

    auth.user = makeUser([SUPERUSER_PERMISSION]);
    expect(catalog.services.value.some((s) => s.slug === "ai-chat")).toBe(true);
  });

  it("clearPlatformCatalog resets loaded so the next load refetches", async () => {
    vi.mocked(api.get).mockResolvedValue({ data: catalogPayload });

    const first = usePlatformCatalog();
    await first.load();
    expect(api.get).toHaveBeenCalledTimes(1);

    await first.load();
    expect(api.get).toHaveBeenCalledTimes(1);

    clearPlatformCatalog();

    const second = usePlatformCatalog();
    await second.load();
    expect(api.get).toHaveBeenCalledTimes(2);
  });

  it("falls back to static catalog when the API fails", async () => {
    vi.mocked(api.get).mockRejectedValue(new Error("network"));

    const auth = useAuthStore();
    auth.user = makeUser([SUPERUSER_PERMISSION]);

    const catalog = usePlatformCatalog();
    await catalog.load();

    expect(catalog.services.value.some((s) => s.slug === "ai-chat")).toBe(true);
    expect(catalog.services.value.some((s) => s.slug === "tasks")).toBe(true);
  });
});
