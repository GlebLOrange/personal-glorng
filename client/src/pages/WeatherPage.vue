<script setup lang="ts">
import PageShell from "@/components/layout/PageShell.vue";
import { Card } from "@/components/ui/card";
import EmptyState from "@/components/ui/EmptyState.vue";
import WeatherLocationCard from "@/components/weather/WeatherLocationCard.vue";
import WeatherLocationForm from "@/components/weather/WeatherLocationForm.vue";
import { useActiveWeatherQuery } from "@/composables/useActiveWeatherQuery";
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
const { activeQuery, setActiveQuery } = useActiveWeatherQuery();
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

function handleSelect(query: string): void {
  setActiveQuery(query);
}
</script>

<template>
  <PageShell
    :title="WEATHER_TOOL_NAME"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'weather' }]"
    body-class="font-mono"
  >
    <header class="page-intro">
      <p class="text-sm text-surface-mid">
        Local time and conditions for your cities. Click a city to show it in the page header.
      </p>
    </header>

    <section class="mb-8 min-w-0">
      <h2 class="text-lg font-bold text-surface-light mb-4">your cities</h2>
      <WeatherLocationForm
        :add-location="handleAdd"
        :disabled="!canAddLocation"
        :helper-text="guestLimitMessage"
      />
    </section>

    <section class="min-w-0">
      <div
        v-if="loading || seeding"
        class="grid min-w-0 grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3"
        aria-busy="true"
        aria-label="Loading cities"
      >
        <Card v-for="n in 3" :key="n" variant="compact" class="animate-pulse">
          <div class="h-4 w-24 bg-surface-border rounded mb-2" />
          <div class="h-3 w-40 bg-surface-border rounded" />
        </Card>
      </div>

      <EmptyState
        v-else-if="locations.length === 0"
        description="No cities yet. Search above to add your first location."
      />

      <div v-else class="grid min-w-0 grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
        <WeatherLocationCard
          v-for="loc in locations"
          :key="loc.id"
          :label="loc.label"
          :query="loc.query"
          :active="loc.query.toLowerCase() === activeQuery.toLowerCase()"
          selectable
          :removable="!isDefaultLocation(loc)"
          @select="handleSelect(loc.query)"
          @remove="handleRemove(loc.id)"
        />
      </div>
    </section>
  </PageShell>
</template>
