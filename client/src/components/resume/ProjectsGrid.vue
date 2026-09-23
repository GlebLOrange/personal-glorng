<script setup lang="ts">
import { RouterLink } from "vue-router";

import { Card } from "@/components/ui/card";
import type { Project } from "@/types";

defineProps<{
  projects: Project[];
}>();

function isExternal(url: string): boolean {
  return /^https?:\/\//i.test(url);
}
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <Card v-for="proj in projects" :key="proj.name" :hoverable="Boolean(proj.url)">
      <h3 class="card-title mb-1">
        <a
          v-if="proj.url && isExternal(proj.url)"
          :href="proj.url"
          target="_blank"
          rel="noopener noreferrer"
          class="text-inherit underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
        >
          {{ proj.name }}
          <span class="sr-only">(opens in new tab)</span>
        </a>
        <RouterLink
          v-else-if="proj.url"
          :to="proj.url"
          class="text-inherit underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
        >
          {{ proj.name }}
        </RouterLink>
        <span v-else>{{ proj.name }}</span>
      </h3>
      <p class="text-body mb-4">{{ proj.description }}</p>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="t in proj.tech"
          :key="t"
          class="text-sm text-surface-sage"
        >
          {{ t }}
        </span>
      </div>
    </Card>
  </div>
</template>
