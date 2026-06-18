export const isFirebaseEnabled =
  import.meta.env.VITE_FIREBASE_ENABLED === "true" &&
  Boolean(import.meta.env.VITE_FIREBASE_API_KEY) &&
  Boolean(import.meta.env.VITE_FIREBASE_AUTH_DOMAIN) &&
  Boolean(import.meta.env.VITE_FIREBASE_PROJECT_ID) &&
  Boolean(import.meta.env.VITE_FIREBASE_APP_ID);

export const isFirebaseAnalyticsEnabled =
  isFirebaseEnabled && Boolean(import.meta.env.VITE_FIREBASE_MEASUREMENT_ID);
