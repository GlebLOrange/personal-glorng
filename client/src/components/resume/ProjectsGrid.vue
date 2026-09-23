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
    <template v-for="proj in projects" :key="proj.name">
      <Card
        v-if="proj.url && isExternal(proj.url)"
        as="a"
        :href="proj.url"
        target="_blank"
        rel="noopener noreferrer"
        hoverable
      >
        <h3 class="card-title mb-1">
          {{ proj.name }}
          <span class="sr-only">(opens in new tab)</span>
        </h3>
        <p class="text-body mb-4">{{ proj.description }}</p>
        <div class="flex flex-wrap gap-2">
          <span v-for="t in proj.tech" :key="t" class="inline-flex items-center rounded-lg bg-surface-dark px-2.5 py-1 text-sm text-surface-sage">
            {{ t }}
          </span>
        </div>
      </Card>
      <RouterLink
        v-else-if="proj.url"
        v-slot="{ href, navigate }"
        :to="proj.url"
        custom
      >
        <Card as="a" :href="href" hoverable @click="navigate">
          <h3 class="card-title mb-1">{{ proj.name }}</h3>
          <p class="text-body mb-4">{{ proj.description }}</p>
          <div class="flex flex-wrap gap-2">
            <span v-for="t in proj.tech" :key="t" class="inline-flex items-center rounded-lg bg-surface-dark px-2.5 py-1 text-sm text-surface-sage">
              {{ t }}
            </span>
          </div>
        </Card>
      </RouterLink>
      <Card v-else>
        <h3 class="card-title mb-1">{{ proj.name }}</h3>
        <p class="text-body mb-4">{{ proj.description }}</p>
        <div class="flex flex-wrap gap-2">
          <span v-for="t in proj.tech" :key="t" class="inline-flex items-center rounded-lg bg-surface-dark px-2.5 py-1 text-sm text-surface-sage">
            {{ t }}
          </span>
        </div>
      </Card>
    </template>
  </div>
</template>
