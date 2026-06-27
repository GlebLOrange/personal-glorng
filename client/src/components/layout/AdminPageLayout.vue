<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import AdminBreadcrumbs from "@/components/layout/AdminBreadcrumbs.vue";
import BackLink from "@/components/ui/BackLink.vue";
import { formatBreadcrumbLabel } from "@/utils/format";

const props = withDefaults(
  defineProps<{
    title: string;
    maxWidth?: "sm" | "md" | "lg" | "xl";
    backTo?: RouteLocationRaw;
    backLabel?: string;
  }>(),
  {
    backTo: "/admin",
    backLabel: "Back to tools",
  },
);

const breadcrumbLabel = computed(() => formatBreadcrumbLabel(props.title));
</script>

<template>
  <div
    :class="[
      'mx-auto px-6 py-16',
      maxWidth === 'sm'
        ? 'max-w-sm'
        : maxWidth === 'md'
          ? 'max-w-3xl'
          : maxWidth === 'xl'
            ? 'max-w-5xl'
            : 'max-w-3xl',
    ]"
  >
    <AdminBreadcrumbs :current-label="breadcrumbLabel" />
    <div class="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <h1 class="text-2xl font-bold text-surface-light">
        <span class="accent-gradient">€ {{ title }}</span>
      </h1>
      <BackLink :to="backTo" :label="backLabel" />
    </div>
    <slot />
  </div>
</template>
