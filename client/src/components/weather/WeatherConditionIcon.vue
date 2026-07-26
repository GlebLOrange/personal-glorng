<script setup lang="ts">
import type { WeatherConditionKind } from "@/utils/weather";

withDefaults(
  defineProps<{
    kind: WeatherConditionKind;
    className?: string;
  }>(),
  { className: "size-4" },
);
</script>

<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    :class="[className, 'shrink-0']"
  >
    <template v-if="kind === 'clear'">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </template>
    <template v-else-if="kind === 'partly'">
      <circle cx="8" cy="9" r="3" />
      <path d="M8 2v1.5M3.5 5.5l1 1M2 10h1.5" />
      <path d="M17 14a4 4 0 0 0-7.5-1.8A3.5 3.5 0 1 0 10 20h7a3 3 0 0 0 0-6z" />
    </template>
    <template v-else-if="kind === 'cloud'">
      <path d="M17 18a4 4 0 0 0 0-8 5.5 5.5 0 0 0-10.6 1.7A3.5 3.5 0 0 0 7 18h10z" />
    </template>
    <template v-else-if="kind === 'fog'">
      <path d="M5 10h14M4 14h16M7 18h10" />
    </template>
    <template v-else-if="kind === 'rain'">
      <path d="M17 13a4 4 0 0 0 0-8 5.5 5.5 0 0 0-10.6 1.7A3.5 3.5 0 0 0 7 13h10z" />
      <path d="M8 16v3M12 17v3M16 16v3" />
    </template>
    <template v-else-if="kind === 'snow'">
      <path d="M17 13a4 4 0 0 0 0-8 5.5 5.5 0 0 0-10.6 1.7A3.5 3.5 0 0 0 7 13h10z" />
      <path d="M10 16.5 9 18M14 16.5l1 1.5M12 16v2.5" />
    </template>
    <template v-else-if="kind === 'storm'">
      <path d="M17 12a4 4 0 0 0 0-8 5.5 5.5 0 0 0-10.6 1.7A3.5 3.5 0 0 0 7 12h10z" />
      <path d="m11 13-2 4h3l-1.5 4" />
    </template>
    <template v-else>
      <path d="M14 4v10M14 18v2" />
      <circle cx="14" cy="14" r="8" />
    </template>
  </svg>
</template>
