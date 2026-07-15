<script setup lang="ts">
import { Card } from "@/components/ui/card";
import type { Project } from "@/types";
import { safeNavigationHref } from "@/utils/safeUrl";

defineProps<{
  projects: Project[];
}>();
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <Card v-for="(proj, i) in projects" :key="i" hoverable>
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
        v-if="proj.url && safeNavigationHref(proj.url)"
        :href="safeNavigationHref(proj.url) ?? '#'"
        target="_blank"
        rel="noopener noreferrer"
        class="text-sm font-medium text-accent-blue hover:text-accent-violet transition-colors"
      >
        view project &rarr;
      </a>
    </Card>
  </div>
</template>
