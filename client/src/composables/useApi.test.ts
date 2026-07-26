import { AxiosError, type AxiosAdapter, type InternalAxiosRequestConfig } from "axios";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "@/composables/useApi";
import { tryRefreshSession } from "@/utils/authSession";

vi.mock("@/utils/authSession", () => ({
  tryRefreshSession: vi.fn(),
}));

const refreshMock = vi.mocked(tryRefreshSession);

function okResponse(config: InternalAxiosRequestConfig, data: unknown = { ok: true }) {
  return {
    data,
    status: 200,
    statusText: "OK",
    headers: {},
    config,
  };
}

function reject401(config: InternalAxiosRequestConfig): Promise<never> {
  return Promise.reject(
    new AxiosError("Unauthorized", "ERR_BAD_REQUEST", config, null, {
      data: { detail: "unauthorized" },
      status: 401,
      statusText: "Unauthorized",
      headers: {},
      config,
    }),
  );
}

function rejectStatus(config: InternalAxiosRequestConfig, status: number): Promise<never> {
  return Promise.reject(
    new AxiosError("Request failed", "ERR_BAD_REQUEST", config, null, {
      data: { detail: "error" },
      status,
      statusText: "Error",
      headers: {},
      config,
    }),
  );
}

describe("useApi 401 refresh interceptor", () => {
  const originalAdapter = api.defaults.adapter;

  beforeEach(() => {
    refreshMock.mockReset();
    api.defaults.adapter = originalAdapter;
  });

  afterEach(() => {
    api.defaults.adapter = originalAdapter;
  });

  it("refreshes once then retries a single 401", async () => {
    refreshMock.mockResolvedValue(true);
    let attempts = 0;
    api.defaults.adapter = (async (config) => {
      attempts += 1;
      const retry = Boolean((config as InternalAxiosRequestConfig & { _retry?: boolean })._retry);
      if (!retry) return reject401(config);
      return okResponse(config);
    }) as AxiosAdapter;

    const { data } = await api.get("/tools/ping");
    expect(data).toEqual({ ok: true });
    expect(refreshMock).toHaveBeenCalledTimes(1);
    expect(attempts).toBe(2);
  });

  it("queues concurrent 401s behind a single refresh", async () => {
    let resolveRefresh!: (value: boolean) => void;
    refreshMock.mockImplementation(
      () =>
        new Promise<boolean>((resolve) => {
          resolveRefresh = resolve;
        }),
    );

    api.defaults.adapter = (async (config) => {
      const retry = Boolean((config as InternalAxiosRequestConfig & { _retry?: boolean })._retry);
      if (!retry) return reject401(config);
      return okResponse(config, { path: config.url });
    }) as AxiosAdapter;

    const first = api.get("/tools/a");
    const second = api.get("/tools/b");

    await vi.waitFor(() => expect(refreshMock).toHaveBeenCalledTimes(1));
    resolveRefresh(true);

    const [a, b] = await Promise.all([first, second]);
    expect(a.data).toEqual({ path: "/tools/a" });
    expect(b.data).toEqual({ path: "/tools/b" });
    expect(refreshMock).toHaveBeenCalledTimes(1);
  });

  it("rejects queued requests when refresh fails", async () => {
    refreshMock.mockResolvedValue(false);
    api.defaults.adapter = (async (config) => reject401(config)) as AxiosAdapter;

    await expect(api.get("/tools/ping")).rejects.toMatchObject({
      response: { status: 401 },
    });
    expect(refreshMock).toHaveBeenCalledTimes(1);
  });

  it("does not refresh again on 401 from /auth/refresh", async () => {
    api.defaults.adapter = (async (config) => reject401(config)) as AxiosAdapter;

    await expect(api.post("/auth/refresh")).rejects.toMatchObject({
      response: { status: 401 },
    });
    expect(refreshMock).not.toHaveBeenCalled();
  });

  it("does not refresh on non-401 errors", async () => {
    api.defaults.adapter = (async (config) => rejectStatus(config, 500)) as AxiosAdapter;

    await expect(api.get("/tools/ping")).rejects.toMatchObject({
      response: { status: 500 },
    });
    expect(refreshMock).not.toHaveBeenCalled();
  });
});
