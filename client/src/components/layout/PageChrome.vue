<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { RouteLocationRaw } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
import PageBreadcrumbs from "@/components/layout/PageBreadcrumbs.vue";
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";
import WeatherBar from "@/components/weather/WeatherBar.vue";

withDefaults(
  defineProps<{
    title: string;
    titlePrefix?: string;
    breadcrumbs: BreadcrumbSegment[];
    backTo?: RouteLocationRaw;
  }>(),
  {
    titlePrefix: "",
    backTo: undefined,
  },
);

const showWeatherBar = ref(false);

onMounted(() => {
  window.setTimeout(() => {
    showWeatherBar.value = true;
  }, 250);
});
</script>

<template>
  <div
    class="relative -mx-6 border-b border-surface-border bg-surface-dark/80 px-6 py-1.5 backdrop-blur-md"
  >
    <div class="flex min-w-0 items-stretch gap-3">
      <div class="flex min-w-0 flex-1 flex-col justify-center">
        <div class="page-breadcrumb-row">
          <PageBreadcrumbs :segments="breadcrumbs" class="flex-1" />
          <BackLink v-if="backTo" :to="backTo" size="compact" class="shrink-0" />
        </div>

        <h1
          class="mt-0.5 min-w-0 truncate text-lg font-bold leading-tight text-surface-light"
          :title="`${titlePrefix}${title}`"
        >
          <span class="accent-gradient">{{ titlePrefix }}{{ title }}</span>
        </h1>
      </div>

      <WeatherBar
        v-if="showWeatherBar"
        chrome
        wrapper-class="hidden md:flex w-[var(--tile)] shrink-0 self-stretch"
        card-class="page-chrome-weather-card"
      />
    </div>
  </div>
</template>
