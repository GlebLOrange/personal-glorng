<script setup lang="ts">
import { Card } from "@/components/ui/card";
import { PORTFOLIO_CV_TILE_CLASS } from "@/constants/portfolioSections";
import type { Experience } from "@/types";

defineProps<{
  experience: Experience[];
}>();

const PROOF_COUNT = 3;
</script>

<template>
  <div class="space-y-4">
    <Card
      v-for="exp in experience"
      :key="`${exp.role}-${exp.company}-${exp.period}`"
      variant="compact"
      :class="['min-w-0', PORTFOLIO_CV_TILE_CLASS]"
    >
      <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div class="min-w-0">
          <h3 class="card-title">{{ exp.role }}</h3>
          <p class="text-meta mt-1">{{ exp.company }}</p>
        </div>
        <span class="text-meta shrink-0">
          {{ exp.period }}
        </span>
      </div>
      <p v-if="exp.description" class="text-body mt-3">{{ exp.description }}</p>
      <ul v-if="exp.highlights?.length" class="mt-3 space-y-1">
        <li
          v-for="(highlight, j) in exp.highlights.slice(0, PROOF_COUNT)"
          :key="j"
          class="text-body flex gap-3"
        >
          <span class="text-accent-golden shrink-0" aria-hidden="true">▸</span>
          <span>{{ highlight }}</span>
        </li>
      </ul>
      <details
        v-if="exp.highlights && exp.highlights.length > PROOF_COUNT"
        class="experience-tech-details mt-3"
      >
        <summary
          class="flex min-h-11 cursor-pointer list-none items-center text-sm text-accent-coral outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50 rounded-lg"
        >
          View technical details
        </summary>
        <ul class="mt-3 space-y-1">
          <li
            v-for="(highlight, j) in exp.highlights.slice(PROOF_COUNT)"
            :key="j"
            class="text-body flex gap-3"
          >
            <span class="text-accent-golden shrink-0" aria-hidden="true">▸</span>
            <span>{{ highlight }}</span>
          </li>
        </ul>
      </details>
    </Card>
  </div>
</template>
