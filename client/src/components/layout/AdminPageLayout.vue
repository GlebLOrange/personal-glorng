<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import AdminBreadcrumbs from "@/components/layout/AdminBreadcrumbs.vue";
import { formatBreadcrumbLabel } from "@/utils/format";

const props = defineProps<{
  title: string;
  maxWidth?: "sm" | "md" | "lg" | "xl";
}>();

const route = useRoute();
const showBreadcrumb = computed(() => route.path.startsWith("/admin/tools"));
const breadcrumbLabel = computed(() => formatBreadcrumbLabel(props.title));
</script>

<template>
  <div
    :class="[
      'mx-auto px-6 py-16',
      maxWidth === 'sm' ? 'max-w-sm'
        : maxWidth === 'md' ? 'max-w-3xl'
        : maxWidth === 'xl' ? 'max-w-5xl'
        : 'max-w-3xl',
    ]"
  >
    <AdminBreadcrumbs
      v-if="showBreadcrumb"
      :current-label="breadcrumbLabel"
    />
    <h1 class="text-2xl font-bold text-surface-light mb-8">
      <span class="accent-gradient">€ {{ title }}</span>
    </h1>
    <slot />
  </div>
</template>
