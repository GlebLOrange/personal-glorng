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
  }>(),
  {
    backTo: "/admin",
    hub: "admin",
    maxWidth: "5xl",
  },
);

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
    as="div"
  >
    <slot />
  </PageShell>
</template>
