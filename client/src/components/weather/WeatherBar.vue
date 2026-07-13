<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import { Card } from "@/components/ui/card";
import WeatherSummaryContent from "@/components/weather/WeatherSummaryContent.vue";
import { WEATHER_PATH, WEATHER_ROUTE_NAME, WEATHER_TOOL_NAME } from "@/constants/weather";

const props = withDefaults(
  defineProps<{
    wrapperClass?: string;
    cardClass?: string;
    chrome?: boolean;
  }>(),
  {
    wrapperClass: "",
    cardClass: "page-weather-tile-card",
    chrome: false,
  },
);

const route = useRoute();

const visible = computed(() => route.name !== WEATHER_ROUTE_NAME);

const asideClass = computed(() => [props.wrapperClass]);
</script>

<template>
  <aside v-if="visible" :aria-label="WEATHER_TOOL_NAME" :class="asideClass">
    <RouterLink :to="WEATHER_PATH" class="block w-full">
      <Card hoverable :class="cardClass">
        <WeatherSummaryContent
          align="center"
          interactive
          :dense="!chrome"
          :size="chrome ? 'chrome' : 'default'"
        />
      </Card>
    </RouterLink>
  </aside>
</template>
