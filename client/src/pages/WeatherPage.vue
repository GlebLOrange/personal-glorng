<script setup lang="ts">
import AdminBreadcrumbs from "@/components/layout/AdminBreadcrumbs.vue";
import WeatherLocationCard from "@/components/weather/WeatherLocationCard.vue";
import WeatherLocationForm from "@/components/weather/WeatherLocationForm.vue";
import WeatherWidget from "@/components/weather/WeatherWidget.vue";
import { DATE_TIME_LOCATION_SECTION } from "@/constants/timeDateWeatherLocation";
import { useWeatherLocations } from "@/composables/useWeatherLocations";
import { useNotify } from "@/composables/useNotify";

const {
  locations,
  loading,
  seeding,
  isDefaultLocation,
  addLocation,
  removeLocation,
  canAddLocation,
  guestLimitMessage,
} = useWeatherLocations();
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
  <div class="max-w-6xl mx-auto px-4 sm:px-6 py-10 font-mono">
    <div class="mb-8">
      <AdminBreadcrumbs :current-label="DATE_TIME_LOCATION_SECTION" />
      <div class="mb-2 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 class="text-3xl font-bold accent-gradient">{{ DATE_TIME_LOCATION_SECTION }}</h1>
        <RouterLink
          to="/tools"
          class="inline-flex w-fit items-center rounded-lg border border-surface-border bg-surface-card px-3 py-1.5 text-xs font-medium text-surface-light transition-all duration-200 hover:border-accent-blue focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
        >
          Back to all tools
        </RouterLink>
      </div>
      <p class="text-sm text-surface-mid mb-4">Local time and conditions for your cities.</p>
      <WeatherWidget compact show-time />
    </div>

    <WeatherLocationForm
      :add-location="handleAdd"
      :disabled="!canAddLocation"
      :helper-text="guestLimitMessage"
      class="mb-8"
    />

    <section class="mb-10">
      <h2 class="text-lg font-bold text-surface-light mb-4">cities</h2>

      <div v-if="loading || seeding" class="text-sm text-surface-mid animate-pulse mb-4">
        Loading cities...
      </div>

      <div v-else-if="locations.length === 0" class="text-sm text-surface-mid mb-4">
        No cities yet. Add one to track its local time and weather.
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <WeatherLocationCard
          v-for="loc in locations"
          :key="loc.id"
          :label="loc.label"
          :query="loc.query"
          :removable="!isDefaultLocation(loc)"
          @remove="handleRemove(loc.id)"
        />
      </div>
    </section>
  </div>
</template>
