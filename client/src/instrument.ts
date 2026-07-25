import { isSentryEnabled } from "@/constants/sentry";
import { scrubSensitiveUrl } from "@/utils/sensitiveUrl";

let sentry: typeof import("@sentry/vue") | null = null;
let sentryInitialized = false;

function scrubSentryEvent<
  T extends {
    request?: { url?: string };
    breadcrumbs?: Array<{ data?: { url?: string }; message?: string }>;
  },
>(event: T): T {
  if (event.request?.url) {
    event.request.url = scrubSensitiveUrl(event.request.url);
  }
  for (const crumb of event.breadcrumbs ?? []) {
    if (crumb.data?.url) {
      crumb.data.url = scrubSensitiveUrl(crumb.data.url);
    }
  }
  return event;
}

export async function initSentry(app: ReturnType<(typeof import("vue"))["createApp"]>) {
  if (!isSentryEnabled || sentryInitialized) return;

  const dsn = import.meta.env.VITE_CLIENT_SENTRY_DSN;
  if (!dsn) return;

  sentry ??= await import("@sentry/vue");

  sentry.init({
    app,
    dsn,
    environment: import.meta.env.MODE,
    release: import.meta.env.VITE_CLIENT_SENTRY_RELEASE || undefined,

    integrations: [
      sentry.browserTracingIntegration(),
      sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],

    tracesSampleRate: import.meta.env.PROD ? 0.2 : 1.0,
    tracePropagationTargets: ["localhost", /^\/api\//],

    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,

    beforeSend(event) {
      return scrubSentryEvent(event);
    },
    beforeSendTransaction(event) {
      return scrubSentryEvent(event);
    },
  });
  sentryInitialized = true;
}

export async function disableSentry(): Promise<void> {
  if (!sentryInitialized || !sentry) return;

  await sentry.close(2000);
  sentryInitialized = false;
}
