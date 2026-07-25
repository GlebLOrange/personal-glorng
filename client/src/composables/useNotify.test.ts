import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useNotify } from "@/composables/useNotify";

function clearToasts(): void {
  const { toasts, dismiss, releaseTileHost } = useNotify();
  for (const t of [...toasts.value]) {
    dismiss(t.id);
  }
  releaseTileHost();
}

describe("useNotify", () => {
  beforeEach(() => {
    clearToasts();
    vi.useFakeTimers();
  });

  afterEach(() => {
    clearToasts();
    vi.useRealTimers();
  });

  it("pushes a lowercased toast and auto-dismisses after duration", () => {
    const { toast, toasts } = useNotify();

    toast("Hello World", "info", 1000);

    expect(toasts.value).toHaveLength(1);
    expect(toasts.value[0]).toMatchObject({
      message: "hello world",
      type: "info",
    });

    vi.advanceTimersByTime(999);
    expect(toasts.value).toHaveLength(1);

    vi.advanceTimersByTime(1);
    expect(toasts.value).toHaveLength(0);
  });

  it("dismiss clears the toast and its timer", () => {
    const { toast, toasts, dismiss } = useNotify();

    toast("gone", "success", 4000);
    const id = toasts.value[0]!.id;
    dismiss(id);

    expect(toasts.value).toHaveLength(0);

    vi.advanceTimersByTime(5000);
    expect(toasts.value).toHaveLength(0);
  });

  it("pause stops auto-dismiss and resume reschedules full duration", () => {
    const { toast, toasts, pause, resume } = useNotify();

    toast("hold", "error", 2000);
    const id = toasts.value[0]!.id;

    vi.advanceTimersByTime(1500);
    pause(id);
    vi.advanceTimersByTime(5000);
    expect(toasts.value).toHaveLength(1);

    resume(id);
    vi.advanceTimersByTime(1999);
    expect(toasts.value).toHaveLength(1);

    vi.advanceTimersByTime(1);
    expect(toasts.value).toHaveLength(0);
  });

  it("defaults error duration to 6s and others to 4s", () => {
    const { toast, toasts } = useNotify();

    toast("err", "error");
    const errorId = toasts.value[0]!.id;
    vi.advanceTimersByTime(5999);
    expect(toasts.value.some((t) => t.id === errorId)).toBe(true);
    vi.advanceTimersByTime(1);
    expect(toasts.value.some((t) => t.id === errorId)).toBe(false);

    toast("ok", "success");
    const successId = toasts.value[0]!.id;
    vi.advanceTimersByTime(3999);
    expect(toasts.value.some((t) => t.id === successId)).toBe(true);
    vi.advanceTimersByTime(1);
    expect(toasts.value.some((t) => t.id === successId)).toBe(false);
  });

  it("claimTileHost and releaseTileHost toggle the tile claim", () => {
    const { tileHostClaimed, claimTileHost, releaseTileHost } = useNotify();

    expect(tileHostClaimed.value).toBe(false);
    claimTileHost();
    expect(tileHostClaimed.value).toBe(true);
    releaseTileHost();
    expect(tileHostClaimed.value).toBe(false);
  });
});
