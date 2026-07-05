<script setup lang="ts">
import { defineAsyncComponent, onMounted, ref } from "vue";

import NavBar from "@/components/layout/NavBar.vue";
import FooterBar from "@/components/layout/FooterBar.vue";
import ScrollControls from "@/components/layout/ScrollControls.vue";
import ToastContainer from "@/components/ui/ToastContainer.vue";

const WeatherBar = defineAsyncComponent(() => import("@/components/weather/WeatherBar.vue"));
const showWeatherBar = ref(false);

onMounted(() => {
  // ponytail: simple delay keeps weather off first paint; use measured idle scheduling if it grows.
  window.setTimeout(() => {
    showWeatherBar.value = true;
  }, 250);
});
</script>

<template>
  <div class="min-h-screen flex flex-col font-sans">
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <NavBar />
    <main id="main-content" class="flex-1" tabindex="-1">
      <WeatherBar v-if="showWeatherBar" />
      <RouterView />
      <ScrollControls />
    </main>
    <FooterBar />
    <ToastContainer />
  </div>
</template>
