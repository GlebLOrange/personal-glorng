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
      <p class="text-body">{{ exp.description }}</p>
    </BaseCard>
  </div>
</template>
