import type { FirebaseApp } from "firebase/app";
import type { Analytics } from "firebase/analytics";
import type { Router } from "vue-router";

import { isFirebaseAnalyticsEnabled, isFirebaseEnabled } from "@/constants/firebase";
import { scrubSensitivePath } from "@/utils/sensitiveUrl";

let app: FirebaseApp | null = null;
let analytics: Analytics | null = null;
let removeAnalyticsRouteHook: (() => void) | null = null;

function firebaseConfig() {
  return {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
  };
}

async function getFirebaseApp(): Promise<FirebaseApp> {
  if (!isFirebaseEnabled) {
    throw new Error("Firebase is not configured");
  }
  const { initializeApp } = await import("firebase/app");
  app ??= initializeApp(firebaseConfig());
  return app;
}

export async function initFirebaseAnalytics(router: Router): Promise<void> {
  if (!isFirebaseAnalyticsEnabled) return;

  const { getAnalytics, logEvent, setAnalyticsCollectionEnabled } =
    await import("firebase/analytics");
  analytics ??= getAnalytics(await getFirebaseApp());
  setAnalyticsCollectionEnabled(analytics, true);

  if (removeAnalyticsRouteHook) return;

  const debugMode = import.meta.env.MODE === "development";
  const emitPageView = (fullPath: string, title?: string): void => {
    if (!analytics) return;
    logEvent(analytics, "page_view", {
      page_path: scrubSensitivePath(fullPath),
      page_title: title,
      ...(debugMode ? { debug_mode: true } : {}),
    });
  };

  const current = router.currentRoute.value;
  emitPageView(current.fullPath, current.name?.toString());
  removeAnalyticsRouteHook = router.afterEach((to) => {
    emitPageView(to.fullPath, to.name?.toString());
  });
}

export async function disableFirebaseAnalytics(): Promise<void> {
  if (!analytics) return;

  const { setAnalyticsCollectionEnabled } = await import("firebase/analytics");
  if (analytics) {
    setAnalyticsCollectionEnabled(analytics, false);
  }

  removeAnalyticsRouteHook?.();
  removeAnalyticsRouteHook = null;
}
