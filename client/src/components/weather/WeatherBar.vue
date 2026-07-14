<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import { useActiveWeatherQuery } from "@/composables/useActiveWeatherQuery";
import { Card } from "@/components/ui/card";
import WeatherSummaryContent from "@/components/weather/WeatherSummaryContent.vue";
import { WEATHER_PATH, WEATHER_ROUTE_NAME, WEATHER_TOOL_NAME } from "@/constants/weather";

const props = withDefaults(
  defineProps<{
    wrapperClass?: string;
    cardClass?: string;
    chrome?: boolean;
    expanded?: boolean;
  }>(),
  {
    wrapperClass: "",
    cardClass: "page-weather-tile-card",
    chrome: false,
    expanded: false,
  },
);

const route = useRoute();
const { activeQuery } = useActiveWeatherQuery();

const isActivePage = computed(
  () => props.expanded || route.name === WEATHER_ROUTE_NAME,
);

const asideClass = computed(() => [props.wrapperClass]);

const linkClass = computed(() => (props.chrome ? "block h-full w-full" : "block w-full"));

const resolvedCardClass = computed(() =>
  isActivePage.value
    ? [props.cardClass, "border-accent-blue bg-accent-blue/10"]
    : props.cardClass,
);

const summaryProps = computed(() => ({
  query: activeQuery.value,
  align: "center" as const,
  interactive: !isActivePage.value,
  dense: !props.chrome,
  size: props.chrome ? ("chrome" as const) : ("default" as const),
}));
</script>

<template>
  <aside :aria-label="WEATHER_TOOL_NAME" :class="asideClass">
    <RouterLink v-if="!isActivePage" :to="WEATHER_PATH" :class="linkClass">
      <Card hoverable :class="resolvedCardClass">
        <WeatherSummaryContent v-bind="summaryProps" />
      </Card>
    </RouterLink>

    <Card v-else :class="resolvedCardClass" aria-current="page">
      <WeatherSummaryContent v-bind="summaryProps" />
    </Card>
  </aside>
</template>
