import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import type { App } from "vue";

import {
  installGlobalErrorHandlers,
  resetGlobalErrorHandlersForTests,
} from "@/utils/globalErrorHandlers";

const mocks = vi.hoisted(() => ({
  toast: vi.fn(),
  captureClientError: vi.fn(),
}));

vi.mock("@/composables/useNotify", () => ({
  useNotify: () => ({ toast: mocks.toast }),
}));

vi.mock("@/instrument", () => ({
  captureClientError: mocks.captureClientError,
}));

describe("installGlobalErrorHandlers", () => {
  const listeners = new Map<string, EventListener>();

  beforeEach(() => {
    mocks.toast.mockClear();
    mocks.captureClientError.mockClear();
    listeners.clear();
    resetGlobalErrorHandlersForTests();
    vi.stubGlobal("addEventListener", (type: string, listener: EventListener) => {
      listeners.set(type, listener);
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sets app.config.errorHandler and reports + toasts once", () => {
    const app = { config: { errorHandler: undefined as App["config"]["errorHandler"] } };

    installGlobalErrorHandlers(app as App);

    const err = new Error("render boom");
    app.config.errorHandler?.(err, null, "render");

    expect(mocks.captureClientError).toHaveBeenCalledWith(err, { info: "render" });
    expect(mocks.toast).toHaveBeenCalledWith("Something went wrong", "error");
  });

  it("listens for unhandledrejection and prevents default", () => {
    const app = { config: { errorHandler: undefined as App["config"]["errorHandler"] } };
    installGlobalErrorHandlers(app as App);

    const reason = new Error("promise boom");
    const event = {
      reason,
      preventDefault: vi.fn(),
    } as unknown as PromiseRejectionEvent;

    listeners.get("unhandledrejection")?.(event);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(mocks.captureClientError).toHaveBeenCalledWith(reason, {
      info: "unhandledrejection",
    });
    expect(mocks.toast).toHaveBeenCalledWith("Something went wrong", "error");
  });

  it("debounces user-facing toast within the cooldown window", () => {
    const app = { config: { errorHandler: undefined as App["config"]["errorHandler"] } };
    installGlobalErrorHandlers(app as App);

    app.config.errorHandler?.(new Error("a"), null, "a");
    app.config.errorHandler?.(new Error("b"), null, "b");

    expect(mocks.toast).toHaveBeenCalledTimes(1);
    expect(mocks.captureClientError).toHaveBeenCalledTimes(2);
  });
});
