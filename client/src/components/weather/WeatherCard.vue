<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import WeatherWidget from "@/components/weather/WeatherWidget.vue";
import { useSiteWeather } from "@/composables/useSiteWeather";
import { useNotify } from "@/composables/useNotify";

const { displayCity, setDisplayCity, saving } = useSiteWeather();
const { toast } = useNotify();
const expanded = ref(false);
const draftCity = ref("");
const root = ref<HTMLElement | null>(null);

function open(): void {
  draftCity.value = displayCity.value ?? "";
  expanded.value = true;
}

function close(): void {
  expanded.value = false;
  draftCity.value = displayCity.value ?? "";
}

async function applyCity(): Promise<void> {
  if (!draftCity.value.trim()) {
    return;
  }
  try {
    await setDisplayCity(draftCity.value);
    toast("Display city updated", "success");
    close();
  } catch {
    toast("Failed to update city", "error");
  }
}

function onDocumentClick(event: MouseEvent): void {
  if (!expanded.value || !root.value) {
    return;
  }
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

      <form
        v-if="expanded"
        class="flex flex-col gap-2 mt-3 mb-3"
        @submit.prevent="applyCity"
        @click.stop
      >
        <BaseInput v-model="draftCity" placeholder="City name" />
        <BaseButton
          type="submit"
          variant="primary"
          size="sm"
          class="w-full"
          :disabled="saving"
        >
          {{ saving ? "..." : "Change city" }}
        </BaseButton>
      </form>

      <div class="mt-1">
        <WeatherWidget compact />
      </div>
    </BaseCard>
  </div>
</template>
