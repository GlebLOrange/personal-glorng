<script setup lang="ts">
import BaseCard from "@/components/ui/BaseCard.vue";
import type { Experience } from "@/types";

defineProps<{
  experience: Experience[];
}>();
</script>

<template>
  <div class="space-y-4">
    <BaseCard v-for="(exp, i) in experience" :key="i" hoverable>
      <div class="flex justify-between items-start mb-2 gap-4">
        <div>
          <h3 class="card-title">{{ exp.role }}</h3>
          <p class="text-base text-accent-blue">{{ exp.company }}</p>
        </div>
        <span class="text-meta shrink-0">{{ exp.period }}</span>
      </div>
      <p class="text-body mb-3">{{ exp.description }}</p>
      <ul v-if="exp.highlights?.length" class="space-y-2">
        <li
          v-for="(highlight, j) in exp.highlights"
          :key="j"
          class="text-body flex gap-2"
        >
          <span class="text-accent-blue shrink-0" aria-hidden="true">▸</span>
          <span>{{ highlight }}</span>
        </li>
      </ul>
    </BaseCard>
  </div>
</template>
