import type { App } from "vue";

import { useNotify } from "@/composables/useNotify";
import { captureClientError } from "@/instrument";

const TOAST_COOLDOWN_MS = 5000;
const GENERIC_MESSAGE = "Something went wrong";

let installed = false;
let lastToastAt = 0;

function notifyUserOnce(): void {
  const now = Date.now();
  if (now - lastToastAt < TOAST_COOLDOWN_MS) return;
  lastToastAt = now;
  useNotify().toast(GENERIC_MESSAGE, "error");
}

/**
 * Thin crash net for render errors and uncaught rejections.
 * Expected API failures stay at call sites (useApiAction / ErrorState).
 */
export function installGlobalErrorHandlers(app: App): void {
  if (installed) return;
  installed = true;

  app.config.errorHandler = (err, _instance, info) => {
    captureClientError(err, { info });
    notifyUserOnce();
  };

  window.addEventListener("unhandledrejection", (event) => {
    event.preventDefault();
    captureClientError(event.reason, { info: "unhandledrejection" });
    notifyUserOnce();
  });
}

/** Test-only reset so suites can re-install cleanly. */
export function resetGlobalErrorHandlersForTests(): void {
  installed = false;
  lastToastAt = 0;
}
