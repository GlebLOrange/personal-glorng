import { describe, expect, it, vi } from "vitest";

import { useApiAction } from "@/composables/useApiAction";

const toast = vi.fn();

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast }),
}));

describe("useApiAction", () => {
  it("sets loading and returns action result on success", async () => {
    const { loading, run } = useApiAction();
    expect(loading.value).toBe(false);

    const promise = run(async () => "ok", { successMessage: "Done" });
    expect(loading.value).toBe(true);

    const result = await promise;
    expect(result).toBe("ok");
    expect(loading.value).toBe(false);
    expect(toast).toHaveBeenCalledWith("Done", "success");
  });

  it("toasts error message and returns undefined on failure", async () => {
    const { run } = useApiAction({ logErrors: false });
    const result = await run(
      async () => {
        throw new Error("boom");
      },
      { errorMessage: "Failed" },
    );

    expect(result).toBeUndefined();
    expect(toast).toHaveBeenCalledWith("boom", "error");
  });
});
