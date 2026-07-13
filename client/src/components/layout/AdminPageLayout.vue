<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import { formatBreadcrumbLabel } from "@/utils/format";

const props = withDefaults(
  defineProps<{
    title: string;
    maxWidth?: "sm" | "md" | "xl";
    backTo?: RouteLocationRaw;
  }>(),
  {
    backTo: "/admin",
  },
);

const breadcrumbLabel = computed(() => formatBreadcrumbLabel(props.title));

const shellMaxWidth = computed((): "sm" | "md" | "5xl" => {
  if (props.maxWidth === "sm") return "sm";
  if (props.maxWidth === "md") return "md";
  if (props.maxWidth === "xl") return "5xl";
  return "md";
});
</script>

<template>
  <PageShell
    :title="title"
    title-prefix="€ "
    :breadcrumbs="[
      { label: 'tools', to: '/admin' },
      { label: breadcrumbLabel },
    ]"
    :back-to="backTo"
    :max-width="shellMaxWidth"
    :narrow="false"
    as="div"
  >
    <slot />
  </PageShell>
</template>
