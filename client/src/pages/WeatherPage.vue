<script setup lang="ts">
import { computed } from "vue";

import WeatherLocationCard from "@/components/weather/WeatherLocationCard.vue";
import WeatherLocationForm from "@/components/weather/WeatherLocationForm.vue";
import { coordsQuery, useGeolocation } from "@/composables/useGeolocation";
import { useWeatherLocations } from "@/composables/useWeatherLocations";
import { useNotify } from "@/composables/useNotify";

const { status, coords, error: geoError, request: requestGeo } = useGeolocation();
const { locations, addLocation, removeLocation } = useWeatherLocations();
const { toast } = useNotify();

const primaryQuery = computed(() => {
  if (coords.value) {
    return coordsQuery(coords.value.lat, coords.value.lon);
  }
  return "";
});

async function handleAdd(label: string, query: string): Promise<void> {
  try {
    await addLocation(label, query);
    toast("Location added", "success");
  } catch (err) {
    const message = err instanceof Error ? err.message : "Failed to add location";
    toast(message, "error");
    throw err;
  }
}

async function handleRemove(id: number | string): Promise<void> {
  try {
    await removeLocation(id);
    toast("Location removed", "success");
  } catch {
    toast("Failed to remove location", "error");
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-6 py-10 font-mono">
    <div class="mb-8">
      <h1 class="text-3xl font-bold accent-gradient mb-2">weather</h1>
      <p class="text-sm text-surface-mid">
        Your location and saved cities with local time and conditions.
      </p>
    </div>

    <section class="mb-10">
      <h2 class="text-lg font-bold text-surface-light mb-4">your location</h2>

      <div v-if="status === 'pending'" class="text-sm text-surface-mid animate-pulse">
        Detecting location...
      </div>

      <div v-else-if="status === 'denied' || status === 'unsupported'" class="space-y-3">
        <p class="text-sm text-accent-golden">
          {{
            geoError ||
            "Location access unavailable. Add a city below to track weather manually."
          }}
        </p>
        <button
          v-if="status === 'denied'"
          type="button"
          class="text-sm text-surface-mid underline hover:text-surface-light"
          @click="requestGeo"
        >
          Try again
        </button>
      </div>

      <WeatherLocationCard
        v-else-if="primaryQuery"
        label="Your location"
        :query="primaryQuery"
      />
    </section>

    <section class="mb-10">
      <h2 class="text-lg font-bold text-surface-light mb-4">saved locations</h2>

      <div v-if="locations.length === 0" class="text-sm text-surface-mid mb-4">
        No saved locations yet. Add a city to track its weather and local time.
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <WeatherLocationCard
          v-for="loc in locations"
          :key="loc.id"
          :label="loc.label"
          :query="loc.query"
          removable
          @remove="handleRemove(loc.id)"
        />
      </div>

      <WeatherLocationForm :add-location="handleAdd" />
    </section>
  </div>
</template>
