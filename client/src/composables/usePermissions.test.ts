import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { usePermissions } from "@/composables/usePermissions";
import { useAuthStore } from "@/stores/auth";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";
import type { UserResponse } from "@/types";

vi.mock("@/utils/featureFlags", () => ({
  isAiChatEnabled: vi.fn(() => true),
}));

import { isAiChatEnabled } from "@/utils/featureFlags";

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

describe("usePermissions", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.mocked(isAiChatEnabled).mockReturnValue(true);
  });

  it("denies everything when unauthenticated", () => {
    const { can, canAccess, canUseAdminHub, isSuperuser } = usePermissions();
    expect(isSuperuser.value).toBe(false);
    expect(can("news", "read")).toBe(false);
    expect(canAccess("news")).toBe(false);
    expect(canUseAdminHub.value).toBe(false);
  });

  it("grants all capabilities to superuser", () => {
    const auth = useAuthStore();
    auth.user = makeUser([SUPERUSER_PERMISSION]);

    const { can, canAccess, canUseAdminHub, isSuperuser } = usePermissions();
    expect(isSuperuser.value).toBe(true);
    expect(can("news", "write")).toBe(true);
    expect(canAccess("data-extract")).toBe(true);
    expect(canUseAdminHub.value).toBe(true);
  });

  it("checks slug:capability keys for regular users", () => {
    const auth = useAuthStore();
    auth.user = makeUser(["news:read", "tasks:write"]);

    const { can, canAccess } = usePermissions();
    expect(can("news", "read")).toBe(true);
    expect(can("news", "write")).toBe(false);
    expect(canAccess("news")).toBe(true);
    expect(canAccess("tasks")).toBe(true);
    expect(canAccess("expenses")).toBe(false);
  });

  it("opens admin hub for feedback capability", () => {
    const auth = useAuthStore();
    auth.user = makeUser(["feedback:read"]);

    const { canUseAdminHub } = usePermissions();
    expect(canUseAdminHub.value).toBe(true);
  });

  it("hides ai-chat from hub when feature flag is off", () => {
    vi.mocked(isAiChatEnabled).mockReturnValue(false);
    const auth = useAuthStore();
    auth.user = makeUser(["ai-chat:read"]);

    const { canUseAdminHub, canAccess } = usePermissions();
    expect(canAccess("ai-chat")).toBe(true);
    expect(canUseAdminHub.value).toBe(false);
  });

  it("never treats api-docs as an admin hub unlock", () => {
    const auth = useAuthStore();
    auth.user = makeUser(["api-docs:read"]);

    const { canUseAdminHub } = usePermissions();
    expect(canUseAdminHub.value).toBe(false);
  });
});
