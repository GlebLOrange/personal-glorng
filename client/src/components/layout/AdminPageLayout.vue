<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import { formatBreadcrumbLabel } from "@/utils/format";
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";

const props = withDefaults(
  defineProps<{
    title: string;
    maxWidth?: "sm" | "md" | "5xl";
    backTo?: RouteLocationRaw;
    /** Breadcrumb root: admin hub or tools hub. */
    hub?: "admin" | "tools";
    /** Optional page help (forwarded to PageShell → chrome ?). */
    description?: string;
    /**
     * Wrap body in page-tool-body. Defaults on for tools hub; off for admin hub
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
  },
);

const useToolBody = computed(() => props.tool ?? props.hub === "tools");

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
    :narrow="false"
    :description="description"
    :tool="useToolBody"
    as="div"
  >
    <slot />
  </PageShell>
</template>
