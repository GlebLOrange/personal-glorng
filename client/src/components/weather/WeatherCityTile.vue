<script setup lang="ts">
import { computed } from "vue";

import { Card } from "@/components/ui/card";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import WeatherSummaryContent from "@/components/weather/WeatherSummaryContent.vue";

const props = withDefaults(
  defineProps<{
    query: string;
    removable?: boolean;
    active?: boolean;
  }>(),
  {
    removable: false,
    active: false,
  },
);

const emit = defineEmits<{
  select: [];
  remove: [];
}>();

const cardClass = computed(() =>
  props.active
    ? "page-weather-tile-card h-full border-accent-blue bg-accent-blue/10"
    : "page-weather-tile-card h-full",
);

function handleRemove(event: MouseEvent): void {
  event.stopPropagation();
  emit("remove");
}
</script>

<template>
  <div class="page-tile relative h-full min-w-0 w-full">
    <button
      type="button"
      class="block h-full min-w-0 w-full text-left"
      :aria-label="props.active ? `${query} (active city)` : `set ${query} as active city`"
      :aria-current="props.active ? 'true' : undefined"
      :aria-selected="props.active ? true : undefined"
      @click="emit('select')"
    >
      <Card :hoverable="!props.active" :class="cardClass">
        <WeatherSummaryContent
          :query="query"
          align="center"
          dense
          :interactive="!props.active"
        />
      </Card>
    </button>
    <IconCloseButton
      v-if="removable"
      class="absolute right-2 top-2 z-10"
      :aria-label="`remove ${query}`"
      @click="handleRemove"
    />
  </div>
</template>
