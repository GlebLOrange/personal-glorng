import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ref } from "vue";

import { emptyForm, formFromArticle, useNewsAdmin } from "@/composables/useNewsAdmin";
import { useAuthStore } from "@/stores/auth";
import type { NewsArticle, UserResponse } from "@/types";

const loadNews = vi.fn(async () => undefined);
const loadSources = vi.fn(async () => undefined);
const page = ref(1);

vi.mock("vue-router", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/composables/useNews", () => ({
  useNews: () => ({
    articles: ref([]),
    sources: ref([]),
    page,
    total: ref(0),
    totalPages: ref(0),
    listLoading: ref(false),
    listError: ref(null),
    actionLoading: ref(false),
    hasNextPage: ref(false),
    hasPreviousPage: ref(false),
    loadNews,
    loadSources,
    goToPage: vi.fn(),
    ingestNews: vi.fn(),
    loadArticleMetadata: vi.fn(),
    createArticle: vi.fn(),
    updateArticle: vi.fn(),
    deleteArticle: vi.fn(),
    repostToTelegram: vi.fn(),
  }),
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: vi.fn() }),
}));

vi.mock("@/composables/useScrollListFingerprint", () => ({
  useScrollListFingerprint: vi.fn(),
}));

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

function makeArticle(overrides: Partial<NewsArticle> = {}): NewsArticle {
  return {
    id: 1,
    slug: "hello",
    status: "draft",
    source_id: null,
    source_name: "BBC",
    source_url: "https://example.com/a",
    source_feed_url: "",
    source_published_at: null,
    original_title: "Hello",
    title: "Hello",
    summary: "Summary",
    bullets: [],
    themes: ["world"],
    language: "en",
    published_at: null,
    telegram_message_id: null,
    ai_model: null,
    ai_input_hash: null,
    ingest_error: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...overrides,
  };
}

describe("emptyForm / formFromArticle", () => {
  it("builds a blank draft form", () => {
    expect(emptyForm().status).toBe("draft");
    expect(emptyForm().themes).toBe("world");
  });

  it("maps article fields into form data", () => {
    const form = formFromArticle(
      makeArticle({
        themes: ["tech", "world"],
        source_published_at: "2026-01-02T15:30:00Z",
        telegram_message_id: 42,
      }),
    );
    expect(form.themes).toBe("tech, world");
    expect(form.source_published_at).toBe("2026-01-02T15:30");
    expect(form.telegram_message_id).toBe("42");
  });
});

describe("useNewsAdmin", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    loadNews.mockClear();
    loadSources.mockClear();
    page.value = 1;
    useAuthStore().user = makeUser(["news:write", "news-sources:read"]);
  });

  it("sets status filter and reloads admin news", async () => {
    const { setStatusFilter, statusFilter, page: adminPage, reloadAdminNews } = useNewsAdmin();
    await reloadAdminNews();
    expect(loadNews).toHaveBeenCalledWith({ admin: true, status: undefined });

    adminPage.value = 2;
    setStatusFilter("published");
    expect(statusFilter.value).toBe("published");
    expect(adminPage.value).toBe(1);
    await vi.waitFor(() =>
      expect(loadNews).toHaveBeenCalledWith({ admin: true, status: "published" }),
    );
  });

  it("opens create drawer with empty form", () => {
    const { openCreate, drawerOpen, drawerMode, form } = useNewsAdmin();
    form.value.title = "stale";
    openCreate();
    expect(drawerOpen.value).toBe(true);
    expect(drawerMode.value).toBe("create");
    expect(form.value.title).toBe("");
  });
});
