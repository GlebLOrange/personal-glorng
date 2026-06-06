<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import { clockHandAngles, localTimeFromOffset } from "@/utils/weather";

const props = withDefaults(
  defineProps<{
    utcOffsetHours: number | null;
    size?: number;
  }>(),
  { size: 120 },
);

const handAngles = ref({ hour: 0, minute: 0, second: 0 });
let timer: ReturnType<typeof setInterval> | null = null;

const numerals = [
  { label: "XII", angle: 0 },
  { label: "I", angle: 30 },
  { label: "II", angle: 60 },
  { label: "III", angle: 90 },
  { label: "IV", angle: 120 },
  { label: "V", angle: 150 },
  { label: "VI", angle: 180 },
  { label: "VII", angle: 210 },
  { label: "VIII", angle: 240 },
  { label: "IX", angle: 270 },
  { label: "X", angle: 300 },
  { label: "XI", angle: 330 },
] as const;

const viewBox = 100;
const center = viewBox / 2;
const radius = 42;

function updateHands(): void {
  if (props.utcOffsetHours === null) {
    return;
  }
  handAngles.value = clockHandAngles(localTimeFromOffset(props.utcOffsetHours));
}

function numeralPosition(angleDeg: number): { x: number; y: number } {
  const rad = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: center + Math.cos(rad) * radius,
    y: center + Math.sin(rad) * radius,
  };
}

const hourTransform = computed(
  () => `rotate(${handAngles.value.hour} ${center} ${center})`,
);
const minuteTransform = computed(
  () => `rotate(${handAngles.value.minute} ${center} ${center})`,
);
const secondTransform = computed(
  () => `rotate(${handAngles.value.second} ${center} ${center})`,
);

onMounted(() => {
  updateHands();
  timer = setInterval(updateHands, 1_000);
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});

watch(
  () => props.utcOffsetHours,
  () => {
    updateHands();
  },
);
</script>

<template>
  <div
    class="shrink-0 rounded-full border border-surface-border bg-surface-card flex items-center justify-center"
    :style="{ width: `${size}px`, height: `${size}px` }"
    role="img"
    :aria-label="utcOffsetHours !== null ? 'Local analog clock' : 'Clock unavailable'"
  >
    <svg
      v-if="utcOffsetHours !== null"
      :viewBox="`0 0 ${viewBox} ${viewBox}`"
      class="w-[88%] h-[88%]"
      aria-hidden="true"
    >
      <circle
        :cx="center"
        :cy="center"
        :r="radius + 4"
        fill="none"
        stroke="currentColor"
        stroke-width="0.75"
        class="text-surface-border"
      />

      <text
        v-for="numeral in numerals"
        :key="numeral.label"
        :x="numeralPosition(numeral.angle).x"
        :y="numeralPosition(numeral.angle).y"
        text-anchor="middle"
        dominant-baseline="central"
        class="fill-surface-mid font-mono"
        font-size="7"
      >
        {{ numeral.label }}
      </text>

      <line
        :x1="center"
        :y1="center"
        :x2="center"
        :y2="center - 22"
        stroke="currentColor"
        stroke-width="2.5"
        stroke-linecap="round"
        class="text-surface-light"
        :transform="hourTransform"
      />
      <line
        :x1="center"
        :y1="center"
        :x2="center"
        :y2="center - 30"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        class="text-accent-blue"
        :transform="minuteTransform"
      />
      <line
        :x1="center"
        :y1="center"
        :x2="center"
        :y2="center - 34"
        stroke="currentColor"
        stroke-width="1"
        stroke-linecap="round"
        class="text-accent-golden"
        :transform="secondTransform"
      />
      <circle :cx="center" :cy="center" r="2.5" class="fill-surface-light" />
    </svg>

    <span v-else class="text-surface-muted font-mono text-lg">—</span>
  </div>
</template>
