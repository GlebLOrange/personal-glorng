<script setup lang="ts">
import WeatherLocationCard from "@/components/weather/WeatherLocationCard.vue";
import WeatherLocationForm from "@/components/weather/WeatherLocationForm.vue";
import { DEFAULT_WEATHER_LOCATION } from "@/constants/weather";
import { useWeatherLocations } from "@/composables/useWeatherLocations";
import { useNotify } from "@/composables/useNotify";

const { locations, addLocation, removeLocation } = useWeatherLocations();
const { toast } = useNotify();

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
      <h1 class="text-3xl font-bold accent-gradient mb-2">clocks</h1>
      <p class="text-sm text-surface-mid">
        Local time and conditions for Wrocław and your saved cities.
      </p>
    </div>

    <section class="mb-10">
      <h2 class="text-lg font-bold text-surface-light mb-4">home</h2>
      <WeatherLocationCard
        :label="DEFAULT_WEATHER_LOCATION.label"
        :query="DEFAULT_WEATHER_LOCATION.query"
      />
    </section>

    <section class="mb-10">
      <h2 class="text-lg font-bold text-surface-light mb-4">other cities</h2>

      <div v-if="locations.length === 0" class="text-sm text-surface-mid mb-4">
        No saved cities yet. Add one to track its local time and weather.
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
