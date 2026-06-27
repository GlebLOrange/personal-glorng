import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import router from "./router";
import "./styles/main.css";

const app = createApp(App);

app.component("BaseImage", BaseImage);

const pinia = createPinia();
app.use(pinia);
app.use(router);

app.mount("#app");

window.setTimeout(() => {
  void import("./composables/useCookieConsent").then(({ setupCookieConsent }) => {
    setupCookieConsent(app);
  });
}, 0);
