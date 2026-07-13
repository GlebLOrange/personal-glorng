<script setup lang="ts">
import { onMounted, ref } from "vue";
import type { RouteLocationRaw } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
import PageBreadcrumbs from "@/components/layout/PageBreadcrumbs.vue";
import WeatherBar from "@/components/weather/WeatherBar.vue";

type BreadcrumbSegment = { label: string; to?: string };

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
    class="relative -mx-6 max-h-20 border-b border-surface-border bg-surface-dark/80 px-6 py-1.5 backdrop-blur-md"
  >
    <div class="page-breadcrumb-row">
      <PageBreadcrumbs :segments="breadcrumbs" class="flex-1" />
      <BackLink v-if="backTo" :to="backTo" size="compact" class="shrink-0" />
    </div>

    <h1
      class="mt-0.5 min-w-0 truncate text-lg font-bold leading-tight text-surface-light md:max-w-[var(--content)]"
    >
      <span class="accent-gradient">{{ titlePrefix }}{{ title }}</span>
    </h1>

    <WeatherBar
      v-if="showWeatherBar"
      chrome
      wrapper-class="hidden md:block absolute right-6 top-0 z-10 mt-[100px] w-[var(--tile)]"
      card-class="page-chrome-weather-card"
    />
  </div>
</template>
