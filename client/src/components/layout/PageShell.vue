<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import PageChrome from "@/components/layout/PageChrome.vue";
import PinnedToolsRow from "@/components/layout/PinnedToolsRow.vue";

export type BreadcrumbSegment = { label: string; to?: RouteLocationRaw };
export type PageBodyWidth = "full" | "content" | "column";

const props = withDefaults(
  defineProps<{
    title: string;
    breadcrumbs: BreadcrumbSegment[];
    backTo?: RouteLocationRaw;
    maxWidth?: "sm" | "md" | "5xl";
    /**
     * Body width inside the shell: full (stretch), content (2-of-3 tiles),
     * column (centred tool/settings panel). Prefer this over narrow/tool.
     */
    bodyWidth?: PageBodyWidth;
    /** @deprecated Prefer bodyWidth="content". */
    narrow?: boolean;
    paddingY?: string;
    as?: "main" | "div";
    bodyClass?: string;
    /** Skip chrome sr-only h1 when the page renders its own visible heading. */
    omitHeading?: boolean;
    /** Optional page help forwarded to chrome as a ? tip. */
    description?: string;
    /** @deprecated Prefer bodyWidth="column". Wrap slot in page-tool-body. */
    tool?: boolean;
  }>(),
  {
    narrow: true,
    maxWidth: "5xl",
    paddingY: "pb-8 md:pb-10",
    as: "div",
    bodyClass: "",
    omitHeading: false,
    description: undefined,
    tool: false,
    bodyWidth: undefined,
  },
);

const resolvedBodyWidth = computed<PageBodyWidth>(() => {
  if (props.bodyWidth) return props.bodyWidth;
  if (props.tool) return "column";
  if (props.narrow) return "content";
  return "full";
});

const shellClass = computed(() => {
  const widthClass =
    props.maxWidth === "sm" ? "max-w-sm" : props.maxWidth === "md" ? "max-w-3xl" : "max-w-5xl";
  return ["page-shell", widthClass, props.paddingY].filter(Boolean);
});

const bodyClass = computed(() => [
  "page-body",
  resolvedBodyWidth.value === "content" && "page-body-content page-body-narrow",
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
      :description="description"
    />
    <div :class="bodyClass">
      <PinnedToolsRow />
      <div v-if="resolvedBodyWidth === 'column'" class="page-tool-body">
        <slot />
      </div>
      <slot v-else />
    </div>
  </component>
</template>
