import { beforeEach, describe, expect, it, vi } from "vitest";

import { useTasks } from "@/composables/useTasks";
import { datetimeLocalValue } from "@/utils/dates";

vi.mock("@/composables/useApi", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
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

describe("useTasks", () => {
  beforeEach(() => {
    vi.mocked(api.get).mockReset();
    vi.mocked(api.post).mockReset();
    vi.mocked(api.patch).mockReset();
  });

  it("openCreate seeds scheduled_at from a selected calendar date", () => {
    const { openCreate, createForm, showCreateForm } = useTasks();
    openCreate("2026-06-15");

    expect(showCreateForm.value).toBe(true);
    expect(createForm.value.title).toBe("");
    expect(createForm.value.scheduled_at.startsWith("2026-06-15T")).toBe(true);
    expect(createForm.value.scheduled_at).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/);
  });

  it("openCreate falls back to now when no seed date is given", () => {
    const before = datetimeLocalValue();
    const { openCreate, createForm } = useTasks();
    openCreate();
    const after = datetimeLocalValue();

    expect(createForm.value.scheduled_at >= before).toBe(true);
    expect(createForm.value.scheduled_at <= after).toBe(true);
  });

  it("createTask sets field errors for missing title and scheduled_at", async () => {
    const { openCreate, createForm, createErrors, createTask } = useTasks();
    openCreate();
    createForm.value.title = "   ";
    createForm.value.scheduled_at = "";

    await createTask();

    expect(createErrors.value.title).toBe("Title is required");
    expect(createErrors.value.scheduled_at).toBe("Scheduled time is required");
    expect(api.post).not.toHaveBeenCalled();
  });

  it("createTask reloads calendar month after a successful create", async () => {
    vi.mocked(api.get).mockImplementation(async (_url, config) => {
      const params = config?.params as { start?: string; end?: string; page?: number };
      if (params?.start && params?.end) {
        return {
          data: {
            items: [{ id: 9, title: "seeded", scheduled_at: "2026-06-15T10:00:00Z", status: "pending" }],
            total: 1,
            pages: 1,
            page: 1,
          },
        };
      }
      if (String(_url).endsWith("/stats")) {
        return {
          data: {
            pending: 0,
            completed: 0,
            not_completed: 0,
            postponed: 0,
            cancelled: 0,
            failed_syncs: 0,
          },
        };
      }
      return { data: { items: [], total: 0, pages: 0, page: 1 } };
    });
    vi.mocked(api.post).mockResolvedValue({ data: undefined });

    const { loadCalendarMonth, openCreate, createForm, createTask, calendarTasks } = useTasks();
    await loadCalendarMonth("2026-06-01T00:00:00.000Z", "2026-07-01T00:00:00.000Z");
    expect(calendarTasks.value).toHaveLength(1);

    openCreate("2026-06-15");
    createForm.value.title = "standup";

    vi.mocked(api.get).mockClear();
    await createTask();

    const calendarGets = vi
      .mocked(api.get)
      .mock.calls.filter(([, config]) => {
        const params = config?.params as { start?: string; end?: string } | undefined;
        return Boolean(params?.start && params?.end);
      });
    expect(calendarGets.length).toBeGreaterThanOrEqual(1);
    expect(api.post).toHaveBeenCalledWith(
      "/tools/tasks",
      expect.objectContaining({ title: "standup" }),
    );
  });
});
