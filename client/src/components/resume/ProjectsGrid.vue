<script setup lang="ts">
import { Card } from "@/components/ui/card";
import type { Project } from "@/types";
import { isExternalHref, safeNavigationHref } from "@/utils/safeUrl";

defineProps<{
  projects: Project[];
}>();

function projectHref(url: string | undefined): string | null {
  return url ? safeNavigationHref(url) : null;
}
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <Card v-for="proj in projects" :key="proj.name" hoverable>
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
        v-if="projectHref(proj.url)"
        :href="projectHref(proj.url)!"
        :target="isExternalHref(projectHref(proj.url)!) ? '_blank' : undefined"
        :rel="isExternalHref(projectHref(proj.url)!) ? 'noopener noreferrer' : undefined"
        class="text-sm font-medium text-accent-blue hover:text-accent-violet transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 rounded"
      >
        view project
        <span v-if="isExternalHref(projectHref(proj.url)!)" class="sr-only">
          (opens in new tab)
        </span>
        &rarr;
      </a>
    </Card>
  </div>
</template>
