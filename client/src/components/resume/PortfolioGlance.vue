<script setup lang="ts">
import { computed } from "vue";

import { Card } from "@/components/ui/card";
import type { ResumeData } from "@/types";
import { buildGlanceStats } from "@/utils/resumeGlance";

const props = defineProps<{
  resume: ResumeData;
}>();

const stats = computed(() => buildGlanceStats(props.resume));
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <Card v-for="stat in stats" :key="stat.label" hoverable>
      <p class="text-label text-accent-blue mb-2">{{ stat.label }}</p>
      <p class="font-data text-3xl font-semibold text-surface-light mb-2">{{ stat.value }}</p>
      <p class="text-meta">{{ stat.detail }}</p>
    </Card>
  </div>
</template>
