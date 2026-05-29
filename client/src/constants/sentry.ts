/** Local dev: set VITE_SENTRY_ENABLED=true to test client Sentry. Production builds stay on unless false. */
export const isSentryEnabled = (() => {
  const dsn = import.meta.env.VITE_CLIENT_SENTRY_DSN;
  if (!dsn) {
    return false;
  }
  if (import.meta.env.DEV) {
    return import.meta.env.VITE_SENTRY_ENABLED === "true";
  }
  return import.meta.env.VITE_SENTRY_ENABLED !== "false";
})();
