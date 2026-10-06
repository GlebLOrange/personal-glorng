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
  <div class="grid grid-cols-1 gap-4">
    <Card v-for="proj in projects" :key="proj.name" class="min-w-0">
      <h3 class="card-title mb-1">
        <a
          v-if="proj.url && isExternal(proj.url)"
          :href="proj.url"
          target="_blank"
          rel="noopener noreferrer"
          class="hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
        >
          {{ proj.name }}
          <span class="sr-only">(opens in new tab)</span>
        </a>
        <RouterLink
          v-else-if="proj.url"
          :to="proj.url"
          class="hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
        >
          {{ proj.name }}
        </RouterLink>
        <span v-else>{{ proj.name }}</span>
      </h3>
      <p class="text-body">{{ proj.description }}</p>

      <dl v-if="proj.problem || proj.approach || proj.result" class="mt-4 space-y-2 text-sm">
        <div v-if="proj.problem">
          <dt class="text-label text-accent-blue">problem</dt>
          <dd class="text-body mt-0.5">{{ proj.problem }}</dd>
        </div>
        <div v-if="proj.approach">
          <dt class="text-label text-accent-blue">approach</dt>
          <dd class="text-body mt-0.5">{{ proj.approach }}</dd>
        </div>
        <div v-if="proj.result">
          <dt class="text-label text-accent-blue">result</dt>
          <dd class="text-body mt-0.5">{{ proj.result }}</dd>
        </div>
      </dl>

      <div class="mt-3 flex flex-wrap gap-2">
        <span
          v-for="t in proj.tech"
          :key="t"
          class="inline-flex items-center rounded-lg bg-surface-dark px-2.5 py-1 text-sm text-surface-sage"
        >
          {{ t }}
        </span>
      </div>
    </Card>
  </div>
</template>
