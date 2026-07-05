<script setup lang="ts">
import { computed } from "vue";

import BackLink from "@/components/ui/BackLink.vue";
import WeatherLocationCard from "@/components/weather/WeatherLocationCard.vue";
import WeatherLocationForm from "@/components/weather/WeatherLocationForm.vue";
import WeatherSummaryCard from "@/components/weather/WeatherSummaryCard.vue";
import { WEATHER_TOOL_NAME } from "@/constants/weather";
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

const defaultLocation = computed(() => locations.value.find((loc) => isDefaultLocation(loc)));

const trackerLocations = computed(() =>
  locations.value.filter((loc) => !isDefaultLocation(loc)),
);

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
  <main class="max-w-5xl mx-auto px-6 py-12 font-mono">
    <header class="mb-10">
      <div class="mb-3 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <h1 class="text-3xl font-bold accent-gradient">{{ WEATHER_TOOL_NAME }}</h1>
        <BackLink to="/tools" />
      </div>
      <p class="text-sm text-surface-mid">Local time and conditions for your cities.</p>
    </header>

    <section class="mb-10">
      <h2 class="text-lg font-bold text-surface-light mb-4">current</h2>
      <div
        v-if="loading || seeding"
        class="bg-surface-card border border-surface-border rounded-xl p-6 text-sm text-surface-mid animate-pulse"
      >
        Loading...
      </div>
      <div
        v-else
        class="bg-surface-card border border-surface-border rounded-xl p-6 md:p-7"
      >
        <WeatherSummaryCard :query="defaultLocation?.query ?? ''" />
      </div>
    </section>

    <section class="mb-10">
      <h2 class="text-lg font-bold text-surface-light mb-4">add city</h2>
      <WeatherLocationForm
        :add-location="handleAdd"
        :disabled="!canAddLocation"
        :helper-text="guestLimitMessage"
      />
    </section>

    <section v-if="trackerLocations.length > 0 || (!loading && !seeding && locations.length > 0)">
      <h2 class="text-lg font-bold text-surface-light mb-4">trackers</h2>

      <div v-if="loading || seeding" class="text-sm text-surface-mid animate-pulse mb-4">
        Loading cities...
      </div>

      <div v-else-if="trackerLocations.length === 0" class="text-sm text-surface-mid mb-4">
        No extra cities yet. Search above to track more locations.
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <WeatherLocationCard
          v-for="loc in trackerLocations"
          :key="loc.id"
          :label="loc.label"
          :query="loc.query"
          removable
          @remove="handleRemove(loc.id)"
        />
      </div>
    </section>
  </main>
</template>
