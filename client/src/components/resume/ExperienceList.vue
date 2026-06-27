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
      <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div class="min-w-0">
          <h3 class="card-title">{{ exp.role }}</h3>
          <p class="text-base text-accent-blue">{{ exp.company }}</p>
        </div>
        <span
          class="inline-flex w-fit shrink-0 rounded-full border border-accent-blue/30 bg-accent-blue/10 px-3 py-1 text-meta text-accent-blue"
        >
          {{ exp.period }}
        </span>
      </div>
      <p v-if="exp.description" class="text-body mt-4">{{ exp.description }}</p>
      <ul v-if="exp.highlights?.length" class="mt-4 space-y-2">
        <li v-for="(highlight, j) in exp.highlights" :key="j" class="text-body flex gap-3">
          <span class="text-accent-blue shrink-0" aria-hidden="true">▸</span>
          <span>{{ highlight }}</span>
        </li>
      </ul>
    </BaseCard>
  </div>
</template>
