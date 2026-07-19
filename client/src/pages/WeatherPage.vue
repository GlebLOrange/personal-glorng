<script setup lang="ts">
import PageShell from "@/components/layout/PageShell.vue";
import WeatherLocationForm from "@/components/weather/WeatherLocationForm.vue";
import WeatherPinnedCitiesRow from "@/components/weather/WeatherPinnedCitiesRow.vue";
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
    :narrow="false"
    body-class="font-mono"
  >
    <section class="mb-8 min-w-0">
      <h2 class="text-lg font-bold text-surface-light mb-4">your cities</h2>
      <WeatherLocationForm
        :add-location="handleAdd"
        :disabled="!canAddLocation"
        :helper-text="guestLimitMessage"
      />
    </section>

    <WeatherPinnedCitiesRow
      :locations="locations"
      :active-query="activeQuery"
      :loading="loading"
      :seeding="seeding"
      :is-default-location="isDefaultLocation"
      @select="handleSelect"
      @remove="handleRemove"
    />
  </PageShell>
</template>
