<script setup lang="ts">
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";
import { displayBreadcrumbLabel } from "@/utils/format";

withDefaults(
  defineProps<{
    segments: BreadcrumbSegment[];
    /** Larger accent styling for sole section labels (news / admin / settings). */
    elevated?: boolean;
  }>(),
  { elevated: false },
);

function crumbLabel(label: string): string {
  return displayBreadcrumbLabel(label);
}
</script>

<template>
  <nav aria-label="Breadcrumb" class="page-breadcrumb min-w-0">
    <ol class="flex items-center gap-2">
      <li
        v-for="(seg, idx) in segments"
        :key="`${idx}:${seg.label}`"
        class="flex items-center gap-2"
      >
        <!-- ponytail: gradient on inner span — clip/fill on <a> can eat clicks -->
        <RouterLink
          v-if="seg.to"
          :to="seg.to"
          class="relative z-10 inline-flex min-h-11 cursor-pointer items-center"
        >
          <span
            :class="
              elevated
                ? 'truncate text-lg font-bold leading-tight accent-gradient transition-opacity hover:opacity-90'
                : 'page-breadcrumb text-surface-mid transition-colors hover:text-accent-blue'
            "
          >
            {{ crumbLabel(seg.label) }}
          </span>
        </RouterLink>
        <span
          v-else
          :class="
            elevated
              ? 'inline-flex min-h-11 items-center truncate text-lg font-bold leading-tight accent-gradient'
              : 'page-breadcrumb text-surface-light'
          "
          aria-current="page"
        >
          {{ crumbLabel(seg.label) }}
        </span>
        <span
          v-if="idx < segments.length - 1"
          class="page-breadcrumb text-surface-muted"
          aria-hidden="true"
          >/</span
        >
      </li>
    </ol>
  </nav>
</template>
