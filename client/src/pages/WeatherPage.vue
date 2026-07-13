<script setup lang="ts">
import { computed } from "vue";

import PageShell from "@/components/layout/PageShell.vue";
import { Card } from "@/components/ui/card";
import WeatherLocationCard from "@/components/weather/WeatherLocationCard.vue";
import WeatherLocationForm from "@/components/weather/WeatherLocationForm.vue";
import WeatherSummaryContent from "@/components/weather/WeatherSummaryContent.vue";
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
  <PageShell
    :title="WEATHER_TOOL_NAME"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'weather' }]"
    body-class="font-mono"
  >
    <header class="page-intro">
      <p class="text-sm text-surface-mid">Local time and conditions for your cities.</p>
    </header>

    <section class="mb-10 min-w-0">
      <h2 class="text-lg font-bold text-surface-light mb-4">current</h2>
      <Card v-if="loading || seeding" class="text-sm text-surface-mid animate-pulse font-mono">
        Loading...
      </Card>
      <Card v-else class="min-w-0 font-mono">
        <WeatherSummaryContent :query="defaultLocation?.query ?? ''" />
      </Card>
    </section>

    <section class="mb-10 min-w-0">
      <h2 class="text-lg font-bold text-surface-light mb-4">add city</h2>
      <WeatherLocationForm
        :add-location="handleAdd"
        :disabled="!canAddLocation"
        :helper-text="guestLimitMessage"
      />
    </section>

    <section
      v-if="trackerLocations.length > 0 || (!loading && !seeding && locations.length > 0)"
      class="min-w-0"
    >
      <h2 class="text-lg font-bold text-surface-light mb-4">trackers</h2>

      <div v-if="loading || seeding" class="text-sm text-surface-mid animate-pulse mb-4">
        Loading cities...
      </div>

      <div v-else-if="trackerLocations.length === 0" class="text-sm text-surface-mid mb-4">
        No extra cities yet. Search above to track more locations.
      </div>

      <div v-else class="grid min-w-0 grid-cols-1 gap-6">
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
  </PageShell>
</template>
