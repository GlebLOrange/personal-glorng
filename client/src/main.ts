import { createPinia } from "pinia";
import { createApp } from "vue";

// #region agent log
function debugLog(
  hypothesisId: string,
  location: string,
  message: string,
  data: Record<string, unknown>,
): void {
  fetch("http://127.0.0.1:7759/ingest/a59c5ce7-5b46-408d-8a93-dd9a50b51892", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "555cea" },
    body: JSON.stringify({
      sessionId: "555cea",
      runId: "pre-fix",
      hypothesisId,
      location,
      message,
      data,
      timestamp: Date.now(),
    }),
  }).catch(() => {});
}

debugLog("B,D,E", "main.ts:bootstrap", "Vue app bootstrap", {
  href: window.location.href,
  origin: window.location.origin,
  port: window.location.port,
  inIframe: window.self !== window.top,
  viteBehindNginx: import.meta.env.VITE_BEHIND_NGINX ?? null,
  mode: import.meta.env.MODE,
});
// #endregion

import App from "./App.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import { setupCookieConsent } from "./composables/useCookieConsent";
import { restoreAuth } from "./plugins/auth";
import router from "./router";
import "./styles/main.css";

const app = createApp(App);

app.component("BaseImage", BaseImage);

const pinia = createPinia();
app.use(pinia);
app.use(router);

setupCookieConsent(app);

restoreAuth().finally(() => {
  app.mount("#app");
  // #region agent log
  debugLog("B,D", "main.ts:mounted", "Vue app mounted", {
    href: window.location.href,
    route: router.currentRoute.value.fullPath,
  });
  // #endregion
});
