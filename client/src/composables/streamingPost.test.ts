import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { streamingPost, userSafeStreamError } from "@/composables/streamingPost";
import { tryRefreshSession } from "@/utils/authSession";

vi.mock("@/utils/authSession", () => ({
  tryRefreshSession: vi.fn(),
}));

const refreshMock = vi.mocked(tryRefreshSession);

describe("userSafeStreamError", () => {
  it("maps known statuses and admin chat overrides", () => {
    expect(userSafeStreamError(401)).toBe("Please sign in again.");
    expect(userSafeStreamError(503, undefined, { adminChat: true })).toContain("Settings");
    expect(userSafeStreamError(418, "teapot")).toBe("teapot");
  });
});

describe("streamingPost", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    refreshMock.mockReset();
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("retries once after a successful refresh on 401", async () => {
    refreshMock.mockResolvedValue(true);
    fetchMock
      .mockResolvedValueOnce(new Response(null, { status: 401 }))
      .mockResolvedValueOnce(new Response("ok", { status: 200 }));

    const response = await streamingPost("/api/ai/stream", { q: "hi" });
    expect(response.status).toBe(200);
    expect(refreshMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("does not retry when refresh fails", async () => {
    refreshMock.mockResolvedValue(false);
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 401 }));

    const response = await streamingPost("/api/ai/stream", { q: "hi" });
    expect(response.status).toBe(401);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("does not refresh on non-401 responses", async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 500 }));

    const response = await streamingPost("/api/ai/stream", { q: "hi" });
    expect(response.status).toBe(500);
    expect(refreshMock).not.toHaveBeenCalled();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("passes abort signal to fetch", async () => {
    const controller = new AbortController();
    fetchMock.mockResolvedValueOnce(new Response("ok", { status: 200 }));

    await streamingPost("/api/ai/stream", { q: "hi" }, { signal: controller.signal });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/ai/stream",
      expect.objectContaining({ signal: controller.signal }),
    );
  });
});
