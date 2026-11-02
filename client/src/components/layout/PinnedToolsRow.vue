<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import ToastContainer from "@/components/ui/ToastContainer.vue";
import { WEATHER_ROUTE_NAME } from "@/constants/weather";

/** Toast strip on tools hub, admin hub, and public utility routes — not news/settings/nested admin. */
const PINNED_TOOLS_ROUTE_NAMES = new Set<string>([
  "tools",
  "admin",
  WEATHER_ROUTE_NAME,
  "calculator",
  "password-generator",
  "qr-generator",
  "recipes",
  "shortener",
  "vid-download",
  "tool-email",
]);

const route = useRoute();
const showPinnedRow = computed(() => {
  const name = route.name;
  return typeof name === "string" && PINNED_TOOLS_ROUTE_NAMES.has(name);
});
</script>

<template>
  <!-- empty:hidden drops the mb-8 gap when ToastContainer has nothing to show -->
  <div v-if="showPinnedRow" class="page-tool-grid mb-8 min-w-0 empty:hidden">
    <ToastContainer variant="tile" />
  </div>
</template>
