import { initializeApp, type FirebaseApp } from "firebase/app";
import { getAnalytics, logEvent, type Analytics } from "firebase/analytics";
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  type Auth,
  type UserCredential,
} from "firebase/auth";
import type { Router } from "vue-router";

import { isFirebaseAnalyticsEnabled, isFirebaseEnabled } from "@/constants/firebase";

let app: FirebaseApp | null = null;
let auth: Auth | null = null;
let analytics: Analytics | null = null;
let analyticsRouterBound = false;

function firebaseConfig() {
  return {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
    measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
  };
}

function getFirebaseApp(): FirebaseApp {
  if (!isFirebaseEnabled) {
    throw new Error("Firebase is not configured");
  }
  app ??= initializeApp(firebaseConfig());
  return app;
}

export function getFirebaseAuth(): Auth {
  auth ??= getAuth(getFirebaseApp());
  return auth;
}

export async function signInWithGooglePopup(): Promise<UserCredential> {
  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: "select_account" });
  return signInWithPopup(getFirebaseAuth(), provider);
}

export function initFirebaseAnalytics(router: Router): void {
  if (!isFirebaseAnalyticsEnabled || analyticsRouterBound) return;

  analytics ??= getAnalytics(getFirebaseApp());
  analyticsRouterBound = true;

  router.afterEach((to) => {
    if (!analytics) return;
    logEvent(analytics, "page_view", {
      page_path: to.fullPath,
      page_title: to.name?.toString(),
    });
  });
}
