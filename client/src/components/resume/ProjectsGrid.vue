<script setup lang="ts">
import { computed } from "vue";

import { Card } from "@/components/ui/card";
import type { Project } from "@/types";
import { isExternalHref, safeNavigationHref } from "@/utils/safeUrl";

const props = defineProps<{
  projects: Project[];
}>();

const items = computed(() =>
  props.projects.map((proj) => {
    const href = proj.url ? safeNavigationHref(proj.url) : null;
    return {
      proj,
      href,
      external: href ? isExternalHref(href) : false,
    };
  }),
);
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <Card
      v-for="item in items"
      :key="item.proj.name"
      :as="item.href ? 'a' : 'div'"
      :href="item.href ?? undefined"
      :target="item.external ? '_blank' : undefined"
      :rel="item.external ? 'noopener noreferrer' : undefined"
      :hoverable="!!item.href"
      :interactive="!!item.href"
    >
      <h3 class="card-title mb-1">{{ item.proj.name }}</h3>
      <p class="text-body mb-4">{{ item.proj.description }}</p>
      <div class="flex flex-wrap gap-2" :class="item.href ? 'mb-4' : undefined">
        <span
          v-for="t in item.proj.tech"
          :key="t"
          class="px-2.5 py-1 text-sm bg-accent-blue/10 text-accent-blue rounded"
        >
          {{ t }}
        </span>
      </div>
      <span v-if="item.href" class="text-sm font-medium text-accent-blue">
        view project
        <span v-if="item.external" class="sr-only">(opens in new tab)</span>
        &rarr;
      </span>
    </Card>
  </div>
</template>
