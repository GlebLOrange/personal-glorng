<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
import PageBreadcrumbs from "@/components/layout/PageBreadcrumbs.vue";
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";
import { formatBreadcrumbLabel, truncateBreadcrumbTitle } from "@/utils/format";

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

/** Current crumb matches page title — elevated § trail acts as the title. */
const soleSectionCrumb = computed(() => {
  const last = displaySegments.value.at(-1);
  if (!last) return false;
  return formatBreadcrumbLabel(last.label) === formatBreadcrumbLabel(props.title);
});

const showTitle = computed(() => !soleSectionCrumb.value);

const displayTitle = computed(
  () => `${props.titlePrefix}${truncateBreadcrumbTitle(props.title)}`,
);
</script>

<template>
  <div
    class="relative -mx-6 border-b border-surface-border bg-surface-dark/80 px-6 py-1.5 backdrop-blur-md"
  >
    <div class="flex min-h-11 min-w-0 items-center gap-3" :class="backTo ? 'pr-16' : ''">
      <div class="flex min-w-0 flex-1 flex-col justify-center">
        <div
          :class="soleSectionCrumb ? 'flex min-h-11 items-center' : 'page-breadcrumb-row'"
        >
          <PageBreadcrumbs
            :segments="displaySegments"
            :elevated="true"
            class="min-w-0"
          />
        </div>

        <h1
          v-if="showTitle"
          class="mt-0.5 min-w-0 truncate text-lg font-bold leading-tight text-surface-light"
          :title="`${titlePrefix}${title}`"
        >
          <span class="accent-gradient">{{ displayTitle }}</span>
        </h1>
      </div>
    </div>

    <BackLink
      v-if="backTo"
      :to="backTo"
      size="compact"
      class="absolute right-6 top-1/2 -translate-y-1/2"
    />
  </div>
</template>
