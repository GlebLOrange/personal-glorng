import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import { setupCookieConsent } from "./composables/useCookieConsent";
import { restoreAuth } from "./plugins/auth";
import router from "./router";
import "./styles/main.scss";

const app = createApp(App);

app.component("BaseImage", BaseImage);

const pinia = createPinia();
app.use(pinia);
app.use(router);

setupCookieConsent(app);

restoreAuth().finally(() => {
  app.mount("#app");
});
