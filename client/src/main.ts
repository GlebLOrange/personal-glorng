import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import { initColorTheme } from "@/composables/useColorTheme";
import { restoreAuth } from "@/plugins/auth";
import { installGlobalErrorHandlers } from "@/utils/globalErrorHandlers";
import router from "./router";
import "./styles/main.css";

initColorTheme();

const app = createApp(App);

installGlobalErrorHandlers(app);

app.component("BaseImage", BaseImage);

const pinia = createPinia();
app.use(pinia);
app.use(router);

app.mount("#app");

void router.isReady().then(() => restoreAuth());

function loadDeferredFonts(): void {
  void import("@fontsource/ibm-plex-sans/latin-600.css");
  void import("@fontsource/ibm-plex-sans/latin-700.css");
}

if (typeof window !== "undefined" && "requestIdleCallback" in window) {
  window.requestIdleCallback(loadDeferredFonts, { timeout: 3000 });
} else {
  window.setTimeout(loadDeferredFonts, 0);
}

window.setTimeout(() => {
  void import("./composables/useCookieConsent").then(({ setupCookieConsent }) => {
    setupCookieConsent(app);
  });
}, 0);
