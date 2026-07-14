<script setup lang="ts">
import { computed } from "vue";

import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import WeatherSummaryContent from "@/components/weather/WeatherSummaryContent.vue";

const props = defineProps<{
  label: string;
  query: string;
  active?: boolean;
  selectable?: boolean;
  removable?: boolean;
}>();

const emit = defineEmits<{
  remove: [];
  select: [];
}>();

const locationQuery = computed(() => props.query);

const cardClass = computed(() => [
  "font-mono w-full text-left",
  props.active && "border-accent-blue bg-accent-blue/10",
  props.selectable && "cursor-pointer",
]);

function handleClick(): void {
  if (props.selectable) {
    emit("select");
  }
}

function handleRemove(event: MouseEvent): void {
  event.stopPropagation();
  emit("remove");
}
</script>

<template>
  <Card
    as="article"
    variant="compact"
    :interactive="selectable"
    :class="cardClass"
    :tabindex="selectable ? 0 : undefined"
    :aria-current="active ? 'true' : undefined"
    :aria-label="selectable ? `Show ${label} in page header` : undefined"
    @click="handleClick"
    @keydown.enter.prevent="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <CardHeader>
      <CardTitle as="h3" class="flex items-center gap-2 min-w-0">
        <span class="truncate">{{ label }}</span>
        <span
          v-if="active"
          class="shrink-0 rounded-full border border-accent-blue/30 bg-accent-blue/10 px-2 py-0.5 text-[10px] uppercase tracking-wide text-accent-blue"
        >
          in header
        </span>
      </CardTitle>
      <template #actions>
        <button
          v-if="removable"
          type="button"
          class="text-sm text-surface-mid hover:text-accent-golden shrink-0"
          @click="handleRemove"
        >
          Remove
        </button>
      </template>
    </CardHeader>
    <WeatherSummaryContent :query="locationQuery" />
  </Card>
</template>
