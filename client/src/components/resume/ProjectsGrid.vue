<script setup lang="ts">
import { Card } from "@/components/ui/card";
import type { Project } from "@/types";

defineProps<{
  projects: Project[];
}>();
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <Card v-for="proj in projects" :key="proj.name">
      <h3 class="card-title mb-1">{{ proj.name }}</h3>
      <p class="text-body mb-4">{{ proj.description }}</p>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="t in proj.tech"
          :key="t"
          class="px-2.5 py-1 text-sm bg-accent-blue/10 text-accent-blue rounded"
        >
          {{ t }}
        </span>
      </div>
    </Card>
  </div>
</template>
