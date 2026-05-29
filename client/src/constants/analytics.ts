/** Set VITE_GA_ENABLED=true and VITE_GA_ID in env to turn analytics back on. */
export const isAnalyticsEnabled =
  import.meta.env.VITE_GA_ENABLED === "true" && Boolean(import.meta.env.VITE_GA_ID);
