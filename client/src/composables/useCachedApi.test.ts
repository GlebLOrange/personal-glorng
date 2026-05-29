import { ref } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "@/composables/useApi";
import { useCachedApi } from "@/composables/useCachedApi";

vi.mock("@/composables/useApi", () => ({
  api: {
    get: vi.fn(),
  },
}));

describe("useCachedApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetches and stores data on first load", async () => {
    vi.mocked(api.get).mockResolvedValue({ data: { ok: true } });

    const { data, loading, fetch } = useCachedApi<{ ok: boolean }>("/cache-test-a");
    await fetch();

    expect(api.get).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledWith("/cache-test-a");
    expect(data.value).toEqual({ ok: true });
    expect(loading.value).toBe(false);
  });

  it("returns cached data within TTL without refetching", async () => {
    vi.mocked(api.get).mockResolvedValue({ data: { n: 1 } });

    const url = "/cache-test-b";
    const first = useCachedApi<{ n: number }>(url, 60_000);
    await first.fetch();

    const second = useCachedApi<{ n: number }>(url, 60_000);
    await second.fetch();

    expect(api.get).toHaveBeenCalledTimes(1);
    expect(second.data.value).toEqual({ n: 1 });
  });

  it("refetches after TTL expires", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(0);
    vi.mocked(api.get)
      .mockResolvedValueOnce({ data: { v: 1 } })
      .mockResolvedValueOnce({ data: { v: 2 } });

    const url = "/cache-test-c";
    const ttlMs = 1000;
    const first = useCachedApi<{ v: number }>(url, ttlMs);
    await first.fetch();

    vi.setSystemTime(ttlMs + 1);
    const second = useCachedApi<{ v: number }>(url, ttlMs);
    await second.fetch();

    expect(api.get).toHaveBeenCalledTimes(2);
    expect(second.data.value).toEqual({ v: 2 });
    vi.useRealTimers();
  });

  it("resolves reactive url on fetch", async () => {
    vi.mocked(api.get).mockResolvedValue({ data: "x" });
    const path = ref("/cache-test-d");

    const { fetch } = useCachedApi<string>(path);
    await fetch();

    expect(api.get).toHaveBeenCalledWith("/cache-test-d");
  });
});
