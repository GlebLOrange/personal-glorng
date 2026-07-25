import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { blankForm, useNewsSources } from "@/composables/useNewsSources";
import { useAuthStore } from "@/stores/auth";
import type { NewsSource, UserResponse } from "@/types";

const routeParams: { id?: string } = {};
const replace = vi.fn();

vi.mock("vue-router", () => ({
  useRoute: () => ({ params: routeParams }),
  useRouter: () => ({ replace, push: vi.fn() }),
}));

vi.mock("@/composables/useApi", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock("@/composables/useApiAction", () => ({
  useApiAction: () => ({
    loading: { value: false },
    lastError: { value: null },
    run: vi.fn(async (fn: () => Promise<unknown>) => fn()),
  }),
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({
    toast: vi.fn(),
  }),
}));

import { api } from "@/composables/useApi";

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

function makeSource(overrides: Partial<NewsSource> = {}): NewsSource {
  return {
    id: 1,
    name: "BBC",
    feed_url: "https://example.com/rss",
    host: "example.com",
    category: "world",
    region: "global",
    enabled: true,
    last_error: null,
    last_fetched_at: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

describe("blankForm", () => {
  it("returns default create values", () => {
    expect(blankForm()).toEqual({
      name: "",
      feed_url: "",
      category: "world",
      region: "global",
      enabled: true,
    });
  });
});

describe("useNewsSources", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    routeParams.id = undefined;
    replace.mockReset();
    vi.mocked(api.get).mockReset();
    vi.mocked(api.post).mockReset();
    useAuthStore().user = makeUser(["news-sources:write"]);
  });

  it("loads sources via loadSources", async () => {
    vi.mocked(api.get).mockResolvedValue({
      data: { items: [makeSource()], total: 1, pages: 1, page: 1 },
    });

    const { sources, loadError, loadSources } = useNewsSources();
    await loadSources();
    expect(sources.value).toHaveLength(1);
    expect(loadError.value).toBe(false);
    expect(api.get).toHaveBeenCalledWith(
      "/tools/news/sources",
      expect.objectContaining({
        params: expect.objectContaining({ page: 1 }),
      }),
    );
  });

  it("opens create drawer and resets form", () => {
    vi.mocked(api.get).mockResolvedValue({
      data: { items: [], total: 0, pages: 0, page: 1 },
    });

    const { openCreate, drawerOpen, drawerMode, form } = useNewsSources();
    form.value.name = "stale";
    openCreate();
    expect(drawerOpen.value).toBe(true);
    expect(drawerMode.value).toBe("create");
    expect(form.value.name).toBe("");
  });

  it("filters enabled sources and resets page", async () => {
    vi.mocked(api.get).mockResolvedValue({
      data: { items: [makeSource()], total: 1, pages: 1, page: 1 },
    });

    const { setEnabledFilter, enabledFilter, page, loadSources } = useNewsSources();
    await loadSources();

    page.value = 3;
    setEnabledFilter("enabled");
    expect(enabledFilter.value).toBe("enabled");
    expect(page.value).toBe(1);
    await vi.waitFor(() =>
      expect(api.get).toHaveBeenCalledWith(
        "/tools/news/sources",
        expect.objectContaining({
          params: expect.objectContaining({ enabled: true, page: 1 }),
        }),
      ),
    );
  });
});
