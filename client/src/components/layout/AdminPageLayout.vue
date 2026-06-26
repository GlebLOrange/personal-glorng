<script setup lang="ts">
import { computed } from "vue";

import AdminBreadcrumbs from "@/components/layout/AdminBreadcrumbs.vue";
import { formatBreadcrumbLabel } from "@/utils/format";

const props = defineProps<{
  title: string;
  maxWidth?: "sm" | "md" | "lg" | "xl";
}>();

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
      <RouterLink
        to="/tools"
        class="inline-flex w-fit items-center rounded-lg border border-surface-border bg-surface-card px-3 py-1.5 text-xs font-medium text-surface-light transition-all duration-200 hover:border-accent-blue focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
      >
        Back to tools
      </RouterLink>
    </div>
    <slot />
  </div>
</template>
