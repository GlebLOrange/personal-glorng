import { describe, expect, it, vi } from "vitest";

import { useApiAction } from "@/composables/useApiAction";

const toastMock = vi.fn();

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: toastMock }),
}));

describe("admin tool harness", () => {
  it("exposes loading state and surfaces API errors", async () => {
    const { run, loading, lastError } = useApiAction({
      errorFallback: "Failed to load admin data",
      silent: true,
    });

    expect(loading.value).toBe(false);

    const promise = run(async () => {
      throw { response: { data: { detail: "Server unavailable" } } };
    });
    expect(loading.value).toBe(true);

    const result = await promise;
    expect(result).toBeUndefined();
    expect(loading.value).toBe(false);
    expect(lastError.value).toBe("Server unavailable");
  });

  it("clears lastError on successful run", async () => {
    const { run, lastError } = useApiAction({ silent: true });

    await run(async () => {
      throw new Error("first failure");
    });
    expect(lastError.value).toBeTruthy();

    const value = await run(async () => "ok");
    expect(value).toBe("ok");
    expect(lastError.value).toBeNull();
  });
});
