<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
import PageBreadcrumbs from "@/components/layout/PageBreadcrumbs.vue";
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";

const props = withDefaults(
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

/** Full trail: clickable parents + current page crumb. */
const displaySegments = computed((): BreadcrumbSegment[] => {
  if (props.breadcrumbs.length) return props.breadcrumbs;
  return [{ label: props.title }];
});

const displayTitle = computed(() => `${props.titlePrefix}${props.title}`);
</script>

<template>
  <div class="relative border-b border-surface-border bg-surface-dark/80 backdrop-blur-md">
    <!-- Back parks on this row so it shares the breadcrumb vertical band. -->
    <div class="relative my-[15px] flex min-h-8 min-w-0 items-center gap-3">
      <div class="flex min-w-0 flex-1 flex-col justify-center">
        <div class="flex h-8 items-center">
          <PageBreadcrumbs :segments="displaySegments" :elevated="true" class="min-w-0" />
        </div>
        <!-- Breadcrumbs are the visible chrome title; keep a real h1 for outline/AT -->
        <h1 class="sr-only">{{ displayTitle }}</h1>
      </div>

      <!--
        !-right-6 reaches the shell outer edge (chrome is content-width; nav CB includes px-6).
        top-1/2 centers on this row with the breadcrumbs.
      -->
      <BackLink
        v-if="backTo"
        :to="backTo"
        size="compact"
        class="shell-outside-end !-right-6 top-1/2 -translate-y-1/2"
      />
    </div>
  </div>
</template>
