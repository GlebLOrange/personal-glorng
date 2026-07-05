<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import { Card } from "@/components/ui/card";
import WeatherSummaryContent from "@/components/weather/WeatherSummaryContent.vue";
import { WEATHER_PATH, WEATHER_ROUTE_NAME, WEATHER_TOOL_NAME } from "@/constants/weather";

withDefaults(
  defineProps<{
    wrapperClass?: string;
  }>(),
  {
    wrapperClass: "",
  },
);

const route = useRoute();

const visible = computed(() => route.name !== WEATHER_ROUTE_NAME);
</script>

<template>
  <aside v-if="visible" :aria-label="WEATHER_TOOL_NAME" :class="wrapperClass">
    <RouterLink :to="WEATHER_PATH" class="block">
      <Card hoverable class="!p-0 px-3 py-2">
        <WeatherSummaryContent align="right" interactive />
      </Card>
    </RouterLink>
  </aside>
</template>
