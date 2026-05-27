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
      <div class="flex justify-between items-start mb-2">
        <div>
          <h3 class="text-surface-light font-bold">{{ exp.role }}</h3>
          <p class="text-accent-blue text-sm">{{ exp.company }}</p>
        </div>
        <span class="text-xs text-surface-mid">{{ exp.period }}</span>
      </div>
      <p class="text-sm text-surface-mid leading-relaxed">{{ exp.description }}</p>
    </BaseCard>
  </div>
</template>
