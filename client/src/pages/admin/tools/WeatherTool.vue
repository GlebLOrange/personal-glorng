<script setup lang="ts">
import { ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { useWeatherCity } from "@/composables/useWeatherCity";
import type { WeatherData } from "@/types";

const { weatherCity, setWeatherCity } = useWeatherCity();
const city = ref(weatherCity.value);
const weather = ref<WeatherData | null>(null);
const loading = ref(false);
const { toast } = useNotify();

async function fetchWeather(): Promise<void> {
  if (!city.value.trim()) return;
  loading.value = true;
  weather.value = null;
  try {
    const { data } = await api.get<WeatherData>(`/tools/weather/${encodeURIComponent(city.value)}`);
    weather.value = data;
    setWeatherCity(city.value);
  } catch (err) {
    console.error(err);
    toast("Failed to fetch weather", "error");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <AdminPageLayout title="weather">
    <form class="flex gap-3 mb-8" @submit.prevent="fetchWeather">
      <BaseInput v-model="city" placeholder="Enter city name..." class="flex-1" />
      <BaseButton variant="primary" :disabled="loading">
        {{ loading ? "..." : "Search" }}
      </BaseButton>
    </form>

    <BaseCard v-if="weather" hoverable>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <div class="text-xs text-surface-mid uppercase mb-1">Location</div>
          <div class="text-surface-light font-bold">
            {{ weather.nearest_area?.[0]?.areaName?.[0]?.value }},
            {{ weather.nearest_area?.[0]?.country?.[0]?.value }}
          </div>
        </div>
        <div>
          <div class="text-xs text-surface-mid uppercase mb-1">Temperature</div>
          <div class="text-3xl font-bold accent-gradient">
            {{ weather.current_condition?.[0]?.temp_C }}°C
          </div>
        </div>
        <div>
          <div class="text-xs text-surface-mid uppercase mb-1">Condition</div>
          <div class="text-surface-light">
            {{ weather.current_condition?.[0]?.weatherDesc?.[0]?.value }}
          </div>
        </div>
        <div>
          <div class="text-xs text-surface-mid uppercase mb-1">Humidity / Wind</div>
          <div class="text-surface-light text-sm">
            {{ weather.current_condition?.[0]?.humidity }}% /
            {{ weather.current_condition?.[0]?.windspeedKmph }} km/h
          </div>
        </div>
      </div>
    </BaseCard>
  </AdminPageLayout>
</template>
