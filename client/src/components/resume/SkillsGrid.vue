<script setup lang="ts">
import BaseCard from "@/components/ui/BaseCard.vue";
import type { SkillGroup } from "@/types";

defineProps<{
  skills: SkillGroup[];
}>();
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <BaseCard v-for="group in skills" :key="group.category" hoverable>
      <h3 class="text-accent-blue text-sm font-bold mb-3 uppercase tracking-wider">
        {{ group.category }}
      </h3>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="item in group.items"
          :key="item"
          class="interactive-surface px-2 py-1 text-xs text-surface-light bg-surface-dark/50"
        >
          {{ item }}
        </span>
      </div>
    </BaseCard>
  </div>
</template>
