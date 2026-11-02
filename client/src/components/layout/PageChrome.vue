<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
import FieldHelp from "@/components/ui/FieldHelp.vue";
import PageBreadcrumbs from "@/components/layout/PageBreadcrumbs.vue";
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";

const props = withDefaults(
  defineProps<{
    title: string;
    breadcrumbs: BreadcrumbSegment[];
    backTo?: RouteLocationRaw;
    /** Skip sr-only h1 when the page renders its own visible heading. */
    omitHeading?: boolean;
    /** Optional page help; shown as ? in the chrome bottom-right. */
    description?: string;
  }>(),
  {
    backTo: undefined,
    omitHeading: false,
    description: undefined,
  },
);

/** Full trail: clickable parents + current page crumb. */
const displaySegments = computed((): BreadcrumbSegment[] => {
  if (props.breadcrumbs.length) return props.breadcrumbs;
  return [{ label: props.title }];
});
</script>

<template>
  <div class="relative border-b border-surface-border bg-surface-dark/80 backdrop-blur-md">
    <!-- Back parks on this row so it shares the breadcrumb vertical band. -->
    <div class="relative my-[15px] flex min-h-10 min-w-0 items-center gap-3">
      <div class="flex min-w-0 flex-1 flex-col justify-center">
        <div class="flex h-10 items-center">
          <PageBreadcrumbs :segments="displaySegments" :elevated="true" class="min-w-0" />
        </div>
        <!-- Breadcrumbs are the visible chrome title; keep a real h1 for outline/AT -->
        <h1 v-if="!omitHeading" class="sr-only">{{ title }}</h1>
      </div>

      <!--
        !-right-6 reaches the shell outer edge (chrome is content-width; nav CB includes px-6).
        top-1/2 centers on this row with the breadcrumbs.
      -->
      <!-- Teleported: chrome's backdrop-blur would trap position:fixed. Same fixed rail as ScrollControls,
           stacked directly above "scroll to next section" (bottom-[8%] + button height + gap). -->
      <Teleport v-if="backTo" to="body">
        <div class="pointer-events-none fixed inset-x-0 bottom-[calc(8%+3.5rem)] z-30 print:hidden">
          <div class="relative mx-auto w-full max-w-5xl px-6">
            <BackLink :to="backTo" class="scroll-rail-end pointer-events-auto" />
          </div>
        </div>
      </Teleport>
    </div>

    <!-- Wrapper owns absolute pins; FieldHelp root is relative for its tip. -->
    <span
      v-if="description"
      data-testid="page-chrome-help"
      class="absolute bottom-2 right-0 inline-flex"
    >
      <FieldHelp size="sm" align="end" placement="top" :text="description" />
    </span>
  </div>
</template>
