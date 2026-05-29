import { isSentryEnabled } from "@/constants/sentry";

export async function initSentry(app: ReturnType<typeof import("vue")["createApp"]>) {
  if (!isSentryEnabled) return;

  const dsn = import.meta.env.VITE_CLIENT_SENTRY_DSN;
  if (!dsn) return;

  const Sentry = await import("@sentry/vue");

  Sentry.init({
    app,
    dsn,
    environment: import.meta.env.MODE,
    release: import.meta.env.VITE_CLIENT_SENTRY_RELEASE || undefined,

    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],

    tracesSampleRate: import.meta.env.PROD ? 0.2 : 1.0,
    tracePropagationTargets: ["localhost", /^\/api\//],

    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  });
}
