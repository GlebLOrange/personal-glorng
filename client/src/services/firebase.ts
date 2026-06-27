import type { FirebaseApp } from "firebase/app";
import type { Analytics } from "firebase/analytics";
import type { Auth, UserCredential } from "firebase/auth";
import type { Router } from "vue-router";

import { isFirebaseAnalyticsEnabled, isFirebaseEnabled } from "@/constants/firebase";

let app: FirebaseApp | null = null;
let auth: Auth | null = null;
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

export async function getFirebaseAuth(): Promise<Auth> {
  const { getAuth } = await import("firebase/auth");
  auth ??= getAuth(await getFirebaseApp());
  return auth;
}

export async function signInWithGooglePopup(): Promise<UserCredential> {
  const { GoogleAuthProvider, signInWithPopup } = await import("firebase/auth");
  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: "select_account" });
  return signInWithPopup(await getFirebaseAuth(), provider);
}

export async function initFirebaseAnalytics(router: Router): Promise<void> {
  if (!isFirebaseAnalyticsEnabled) return;

  const { getAnalytics, logEvent, setAnalyticsCollectionEnabled } =
    await import("firebase/analytics");
  analytics ??= getAnalytics(await getFirebaseApp());
  setAnalyticsCollectionEnabled(analytics, true);

  if (removeAnalyticsRouteHook) return;

  removeAnalyticsRouteHook = router.afterEach((to) => {
    if (!analytics) return;
    logEvent(analytics, "page_view", {
      page_path: to.fullPath,
      page_title: to.name?.toString(),
    });
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
