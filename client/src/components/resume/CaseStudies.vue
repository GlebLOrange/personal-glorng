<script setup lang="ts">
import { RouterLink } from "vue-router";

import type { Project } from "@/types";

defineProps<{
  projects: Project[];
}>();

function isExternal(url: string): boolean {
  return /^https?:\/\//i.test(url);
}
</script>

<template>
  <div class="case-study-list flex flex-col divide-y divide-surface-border/60">
    <details v-for="proj in projects" :key="proj.slug">
      <summary
        class="card-title min-h-11 cursor-pointer rounded-lg px-1 focus-visible:ring-2 focus-visible:ring-accent-blue/50"
      >
        {{ proj.name }}
      </summary>
      <div class="px-1 pb-4">
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

        <p v-if="proj.url" class="mt-3">
          <a
            v-if="isExternal(proj.url)"
            :href="proj.url"
            target="_blank"
            rel="noopener noreferrer"
            class="hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
          >
            {{ proj.url }}
            <span class="sr-only">(opens in new tab)</span>
          </a>
          <RouterLink
            v-else
            :to="proj.url"
            class="hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
          >
            {{ proj.url }}
          </RouterLink>
        </p>
      </div>
    </details>
  </div>
</template>
