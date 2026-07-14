<script setup lang="ts">
import { computed } from "vue";

import EmptyState from "@/components/ui/EmptyState.vue";
import { Card } from "@/components/ui/card";
import WeatherBar from "@/components/weather/WeatherBar.vue";
import WeatherCityTile from "@/components/weather/WeatherCityTile.vue";
import type { GuestWeatherLocation } from "@/composables/useWeatherLocations";
import type { WeatherLocation } from "@/types";

const props = defineProps<{
  locations: Array<WeatherLocation | GuestWeatherLocation>;
  activeQuery: string;
  loading?: boolean;
  seeding?: boolean;
  isDefaultLocation: (loc: WeatherLocation | GuestWeatherLocation) => boolean;
}>();

const emit = defineEmits<{
  select: [query: string];
  remove: [id: number | string];
}>();

const otherCities = computed(() => {
  const active = props.activeQuery.toLowerCase();
  return props.locations
    .filter((loc) => loc.query.toLowerCase() !== active)
    .slice(0, 2);
});

const isBusy = computed(() => props.loading || props.seeding);
</script>

<template>
  <section class="min-w-0">
    <div
      v-if="isBusy"
      class="page-tool-grid min-w-0"
      aria-busy="true"
      aria-label="Loading cities"
    >
      <Card
        v-for="n in 3"
        :key="n"
        variant="compact"
        class="page-tile page-weather-tile-card animate-pulse"
      >
        <div class="mx-auto h-8 w-24 rounded bg-surface-border/60" />
        <div class="mx-auto mt-2 h-4 w-28 rounded bg-surface-border/40" />
      </Card>
    </div>

    <EmptyState
      v-else-if="locations.length === 0"
      description="No cities yet. Search above to add your first location."
    />

    <div v-else class="page-tool-grid min-w-0">
      <WeatherCityTile
        v-for="loc in otherCities"
        :key="loc.id"
        :label="loc.label"
        :query="loc.query"
        :removable="!isDefaultLocation(loc)"
        @select="emit('select', loc.query)"
        @remove="emit('remove', loc.id)"
      />

      <WeatherBar
        wrapper-class="page-tile md:col-start-3"
        card-class="page-weather-tile-card"
        expanded
      />
    </div>
  </section>
</template>
