<script setup lang="ts">
import BaseCard from "@/components/ui/BaseCard.vue";
import type { Project } from "@/types";

defineProps<{
  projects: Project[];
}>();
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <BaseCard v-for="(proj, i) in projects" :key="i" hoverable>
      <h3 class="card-title mb-1">{{ proj.name }}</h3>
      <p class="text-body mb-4">{{ proj.description }}</p>
      <div class="flex flex-wrap gap-2 mb-4">
        <span
          v-for="t in proj.tech"
          :key="t"
          class="px-2.5 py-1 text-sm bg-accent-blue/10 text-accent-blue rounded"
        >
          {{ t }}
        </span>
      </div>
      <a
        v-if="proj.url"
        :href="proj.url"
        target="_blank"
        rel="noopener noreferrer"
        class="text-sm font-medium text-accent-blue hover:text-accent-violet transition-colors"
      >
        View Project &rarr;
      </a>
    </BaseCard>
  </div>
</template>
