<script setup lang="ts">
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";

defineProps<{
  segments: BreadcrumbSegment[];
}>();
</script>

<template>
  <nav aria-label="Breadcrumb" class="page-breadcrumb min-w-0">
    <ol class="flex items-center gap-2">
      <li v-for="(seg, idx) in segments" :key="`${idx}:${seg.label}`" class="flex items-center gap-2">
        <template v-if="seg.to">
          <RouterLink
            :to="seg.to"
            class="page-breadcrumb text-surface-mid transition-colors hover:text-accent-blue"
          >
            {{ seg.label }}
          </RouterLink>
        </template>
        <template v-else>
          <span class="page-breadcrumb text-surface-light" aria-current="page">{{ seg.label }}</span>
        </template>
        <span v-if="idx < segments.length - 1" class="page-breadcrumb text-surface-muted" aria-hidden="true"
          >/</span
        >
      </li>
    </ol>
  </nav>
</template>
