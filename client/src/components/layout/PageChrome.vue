<script setup lang="ts">
import type { RouteLocationRaw } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
import PageBreadcrumbs from "@/components/layout/PageBreadcrumbs.vue";
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";

withDefaults(
  defineProps<{
    title: string;
    titlePrefix?: string;
    breadcrumbs: BreadcrumbSegment[];
    backTo?: RouteLocationRaw;
  }>(),
  {
    titlePrefix: "",
    backTo: undefined,
  },
);
</script>

<template>
  <div
    class="relative -mx-6 border-b border-surface-border bg-surface-dark/80 px-6 py-1.5 backdrop-blur-md"
  >
    <div class="flex min-w-0 items-stretch gap-3">
      <div class="flex min-w-0 flex-1 flex-col justify-center">
        <div class="page-breadcrumb-row">
          <PageBreadcrumbs :segments="breadcrumbs" class="flex-1" />
          <BackLink v-if="backTo" :to="backTo" size="compact" class="shrink-0" />
        </div>

        <h1
          class="mt-0.5 min-w-0 truncate text-lg font-bold leading-tight text-surface-light"
          :title="`${titlePrefix}${title}`"
        >
          <span class="accent-gradient">{{ titlePrefix }}{{ title }}</span>
        </h1>
      </div>
    </div>
  </div>
</template>
