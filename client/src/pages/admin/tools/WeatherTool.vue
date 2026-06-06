<script setup lang="ts">
import { ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import WeatherWidget from "@/components/weather/WeatherWidget.vue";
import { useSiteWeather } from "@/composables/useSiteWeather";
import { useNotify } from "@/composables/useNotify";

const { setDisplayCity, saving } = useSiteWeather();
const { toast } = useNotify();
const searchCity = ref("");
const previewCity = ref<string | undefined>(undefined);

function previewWeather(): void {
  if (!searchCity.value.trim()) {
    return;
  }
  previewCity.value = searchCity.value.trim();
}

async function applyDisplayCity(): Promise<void> {
  const city = previewCity.value ?? searchCity.value;
  if (!city.trim()) {
    return;
  }
  try {
    await setDisplayCity(city);
    toast("Display city updated", "success");
    previewCity.value = undefined;
    searchCity.value = "";
  } catch {
    toast("Failed to update city", "error");
  }
}
</script>

<template>
  <AdminPageLayout title="weather">
    <WeatherWidget class="mb-8" />

    <form class="flex gap-3 mb-4" @submit.prevent="previewWeather">
      <BaseInput
        v-model="searchCity"
        placeholder="Preview another city..."
        class="flex-1"
      />
      <BaseButton variant="primary" type="submit"> Preview </BaseButton>
    </form>

    <WeatherWidget v-if="previewCity" :preview-city="previewCity" class="mb-4" />

    <BaseButton
      v-if="previewCity || searchCity.trim()"
      variant="primary"
      :disabled="saving"
      @click="applyDisplayCity"
    >
      {{ saving ? "..." : "Set as display city" }}
    </BaseButton>
  </AdminPageLayout>
</template>
