<script setup lang="ts">
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";
import { formatBreadcrumbLabel } from "@/utils/format";

const props = withDefaults(
  defineProps<{
    segments: BreadcrumbSegment[];
    /** Title-scale accent on the current crumb only (when it substitutes for h1). */
    elevated?: boolean;
  }>(),
  { elevated: false },
);

function crumbLabel(label: string): string {
  return formatBreadcrumbLabel(label);
}

function isCurrent(idx: number): boolean {
  return idx === props.segments.length - 1;
}

function currentClass(): string {
  if (props.elevated) {
    return "inline-flex h-8 items-center truncate text-lg font-bold leading-none accent-gradient";
  }
  return "page-breadcrumb font-medium text-surface-light";
}

const ancestorClass =
  "page-breadcrumb text-surface-mid transition-colors hover:text-accent-blue";
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
          v-if="seg.to && !isCurrent(idx)"
          :to="seg.to"
          class="relative z-10 inline-flex h-8 cursor-pointer items-center"
        >
          <span :class="ancestorClass">
            {{ crumbLabel(seg.label) }}
          </span>
        </RouterLink>
        <span
          v-else
          :class="currentClass()"
          aria-current="page"
        >
          {{ crumbLabel(seg.label) }}
        </span>
        <span
          v-if="idx < segments.length - 1"
          class="page-breadcrumb inline-flex h-8 items-center text-surface-muted"
          aria-hidden="true"
          >/</span
        >
      </li>
    </ol>
  </nav>
</template>
