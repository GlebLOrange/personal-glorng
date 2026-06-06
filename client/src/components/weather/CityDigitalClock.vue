<script setup lang="ts">
import { computed } from "vue";

import { useLiveLocalTime } from "@/composables/useLiveLocalTime";

const props = defineProps<{
  utcOffsetHours: number | null;
}>();

const offset = computed(() => props.utcOffsetHours);
const { liveTime } = useLiveLocalTime(offset, "time-seconds");
</script>

<template>
  <div
    class="shrink-0 min-w-[9.5rem] rounded-xl border border-surface-border bg-surface-card px-5 py-4 text-center"
    role="timer"
    :aria-label="liveTime ? `Local time ${liveTime}` : 'Clock unavailable'"
  >
    <time
      v-if="liveTime"
      :datetime="liveTime"
      class="block text-4xl md:text-5xl font-bold text-surface-light tabular-nums tracking-tight"
    >
      {{ liveTime }}
    </time>
    <span v-else class="text-surface-muted font-mono text-3xl">—</span>
  </div>
</template>
