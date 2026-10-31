<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import { formatBreadcrumbLabel } from "@/utils/format";
import type { BreadcrumbSegment, PageBodyWidth } from "@/components/layout/PageShell.vue";

const props = withDefaults(
  defineProps<{
    title: string;
    maxWidth?: "sm" | "md" | "5xl";
    backTo?: RouteLocationRaw;
    /** Breadcrumb root: admin hub or tools hub. */
    hub?: "admin" | "tools";
    /** Optional page help (forwarded to PageShell → chrome ?). */
    description?: string;
    /** Body width inside the shell. Defaults to column for tools hub. */
    bodyWidth?: PageBodyWidth;
    /**
     * @deprecated Prefer bodyWidth. Defaults on for tools hub; off for admin hub
     * unless overridden.
     */
    tool?: boolean;
  }>(),
  {
    backTo: "/tools",
    hub: "tools",
    maxWidth: "5xl",
    description: undefined,
    tool: undefined,
    bodyWidth: undefined,
  },
);

const resolvedBodyWidth = computed<PageBodyWidth>(() => {
  if (props.bodyWidth) return props.bodyWidth;
  const useToolBody = props.tool ?? props.hub === "tools";
  return useToolBody ? "column" : "full";
});

const breadcrumbLabel = computed(() => formatBreadcrumbLabel(props.title));

const breadcrumbs = computed((): BreadcrumbSegment[] => {
  const label = breadcrumbLabel.value;
  if (props.hub === "tools") {
    return [{ label: "tools", to: "/tools" }, { label }];
  }
  if (label === "admin") {
    return [{ label: "admin", to: "/admin" }];
  }
  return [{ label: "admin", to: "/admin" }, { label }];
});
</script>

<template>
  <PageShell
    :title="title"
    :breadcrumbs="breadcrumbs"
    :back-to="backTo"
    :max-width="maxWidth"
    :body-width="resolvedBodyWidth"
    :description="description"
    as="div"
  >
    <slot />
  </PageShell>
</template>
