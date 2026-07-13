<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import PageChrome from "@/components/layout/PageChrome.vue";

export type BreadcrumbSegment = { label: string; to?: string };

const props = withDefaults(
  defineProps<{
    title: string;
    titlePrefix?: string;
    breadcrumbs: BreadcrumbSegment[];
    backTo?: RouteLocationRaw;
    maxWidth?: "sm" | "md" | "xl" | "5xl";
    narrow?: boolean;
    paddingY?: string;
    as?: "main" | "div";
    bodyClass?: string;
  }>(),
  {
    titlePrefix: "",
    narrow: true,
    maxWidth: "5xl",
    paddingY: "pb-8 md:pb-10",
    as: "main",
    bodyClass: "",
  },
);

const shellClass = computed(() => {
  const widthClass =
    props.maxWidth === "sm"
      ? "max-w-sm"
      : props.maxWidth === "md"
        ? "max-w-3xl"
        : "max-w-5xl";
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
      :title-prefix="titlePrefix"
      :breadcrumbs="breadcrumbs"
      :back-to="backTo"
    />
    <div :class="bodyClass">
      <slot />
    </div>
  </component>
</template>
