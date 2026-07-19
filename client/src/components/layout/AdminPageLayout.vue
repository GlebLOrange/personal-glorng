<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import { formatBreadcrumbLabel } from "@/utils/format";
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";

const props = withDefaults(
  defineProps<{
    title: string;
    maxWidth?: "sm" | "md" | "xl";
    backTo?: RouteLocationRaw;
    /** Breadcrumb root: admin hub or tools hub. */
    hub?: "admin" | "tools";
    /** Brand prefix on the page title (h1); breadcrumbs always use §. */
    titlePrefix?: string;
  }>(),
  {
    backTo: "/admin",
    hub: "admin",
    maxWidth: "xl",
    titlePrefix: "",
  },
);

const breadcrumbLabel = computed(() => formatBreadcrumbLabel(props.title));

const breadcrumbs = computed((): BreadcrumbSegment[] => {
  const label = breadcrumbLabel.value;
  if (props.hub === "tools") {
    return [
      { label: "tools", to: "/tools" },
      { label },
    ];
  }
  if (label === "admin") {
    return [{ label: "admin", to: "/admin" }];
  }
  return [
    { label: "admin", to: "/admin" },
    { label },
  ];
});

const shellMaxWidth = computed((): "sm" | "md" | "5xl" => {
  if (props.maxWidth === "sm") return "sm";
  if (props.maxWidth === "md") return "md";
  return "5xl";
});
</script>

<template>
  <PageShell
    :title="title"
    :title-prefix="titlePrefix"
    :breadcrumbs="breadcrumbs"
    :back-to="backTo"
    :max-width="shellMaxWidth"
    :narrow="false"
    as="div"
  >
    <slot />
  </PageShell>
</template>
