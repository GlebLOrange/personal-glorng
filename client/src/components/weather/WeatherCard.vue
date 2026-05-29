<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import WeatherWidget from "@/components/weather/WeatherWidget.vue";
import { useWeatherCity } from "@/composables/useWeatherCity";

const { weatherCity, setWeatherCity } = useWeatherCity();
const expanded = ref(false);
const draftCity = ref(weatherCity.value);
const root = ref<HTMLElement | null>(null);

function open(): void {
  draftCity.value = weatherCity.value;
  expanded.value = true;
}

function close(): void {
  expanded.value = false;
  draftCity.value = weatherCity.value;
}

function applyCity(): void {
  if (!draftCity.value.trim()) return;
  setWeatherCity(draftCity.value);
  close();
}

function onDocumentClick(event: MouseEvent): void {
  if (!expanded.value || !root.value) return;
  if (!root.value.contains(event.target as Node)) {
    close();
  }
}

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick);
});
</script>

<template>
  <div ref="root" class="h-full w-full" @click.stop>
    <BaseCard hoverable class="h-full cursor-pointer" @click="!expanded && open()">
      <div class="text-2xl mb-3">☁</div>
      <h3 class="text-surface-light font-bold mb-1">weather</h3>

      <div v-if="expanded" class="space-y-3 mt-3" @click.stop>
        <form class="flex flex-col gap-2" @submit.prevent="applyCity">
          <BaseInput v-model="draftCity" placeholder="City name" />
          <BaseButton type="submit" variant="primary" size="sm" class="w-full"> Update </BaseButton>
        </form>
        <WeatherWidget :city="weatherCity" compact />
      </div>
      <div v-else class="mt-1">
        <WeatherWidget :city="weatherCity" compact />
      </div>
    </BaseCard>
  </div>
</template>
