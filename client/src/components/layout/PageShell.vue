<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import type { RouteLocationRaw } from "vue-router";

import PageChrome from "@/components/layout/PageChrome.vue";
import PinnedToolsRow from "@/components/layout/PinnedToolsRow.vue";
import { introForRoute } from "@/constants/toolIntros";

export type BreadcrumbSegment = { label: string; to?: RouteLocationRaw };

const props = withDefaults(
  defineProps<{
    title: string;
    breadcrumbs: BreadcrumbSegment[];
    backTo?: RouteLocationRaw;
    maxWidth?: "sm" | "md" | "5xl";
    narrow?: boolean;
    paddingY?: string;
    as?: "main" | "div";
    bodyClass?: string;
    /** Skip chrome sr-only h1 when the page renders its own visible heading. */
    omitHeading?: boolean;
  }>(),
  {
    narrow: true,
    maxWidth: "5xl",
    paddingY: "pb-8 md:pb-10",
    as: "div",
    bodyClass: "",
    omitHeading: false,
  },
);

const route = useRoute();
const toolIntro = computed(() => introForRoute(route.name));

const shellClass = computed(() => {
  const widthClass =
    props.maxWidth === "sm" ? "max-w-sm" : props.maxWidth === "md" ? "max-w-3xl" : "max-w-5xl";
  return ["page-shell", widthClass, props.paddingY].filter(Boolean);
});

const bodyClass = computed(() => [
  "page-body",
  props.narrow && "page-body-narrow",
  props.bodyClass,
]);
</script>

<template>
  <component :is="as" :class="shellClass">
    <PageChrome
      :title="title"
      :breadcrumbs="breadcrumbs"
      :back-to="backTo"
      :omit-heading="omitHeading"
    />
    <div :class="bodyClass">
      <PinnedToolsRow />
      <p v-if="toolIntro" class="text-body mb-4 max-w-3xl">{{ toolIntro }}</p>
      <slot />
    </div>
  </component>
</template>
