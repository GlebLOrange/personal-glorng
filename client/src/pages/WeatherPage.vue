<script setup lang="ts">
import WeatherLocationCard from "@/components/weather/WeatherLocationCard.vue";
import WeatherLocationForm from "@/components/weather/WeatherLocationForm.vue";
import { useWeatherLocations } from "@/composables/useWeatherLocations";
import { useNotify } from "@/composables/useNotify";

const { locations, loading, seeding, isDefaultLocation, addLocation, removeLocation } =
  useWeatherLocations();
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
  } catch (err) {
    const message = err instanceof Error ? err.message : "Failed to remove location";
    toast(message, "error");
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-6 py-10 font-mono">
    <div class="mb-8">
      <h1 class="text-3xl font-bold accent-gradient mb-2">clocks</h1>
      <p class="text-sm text-surface-mid">Local time and conditions for your cities.</p>
    </div>

    <section class="mb-10">
      <h2 class="text-lg font-bold text-surface-light mb-4">cities</h2>

      <div v-if="loading || seeding" class="text-sm text-surface-mid animate-pulse mb-4">
        Loading cities...
      </div>

      <div v-else-if="locations.length === 0" class="text-sm text-surface-mid mb-4">
        No cities yet. Add one to track its local time and weather.
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <WeatherLocationCard
          v-for="loc in locations"
          :key="loc.id"
          :label="loc.label"
          :query="loc.query"
          :removable="!isDefaultLocation(loc)"
          @remove="handleRemove(loc.id)"
        />
      </div>

      <WeatherLocationForm :add-location="handleAdd" />
    </section>
  </div>
</template>
