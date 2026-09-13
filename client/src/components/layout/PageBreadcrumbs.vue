<script setup lang="ts">
import ToolIcon from "@/components/icons/ToolIcon.vue";
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";
import { formatBreadcrumbLabel } from "@/utils/format";

const props = withDefaults(
  defineProps<{
    segments: BreadcrumbSegment[];
    /** Title-scale size on the current crumb only (when it substitutes for h1). */
    elevated?: boolean;
  }>(),
  { elevated: false },
);

/** Exact hub labels that get a ToolIcon in the trail. */
const CRUMB_ICONS: Record<string, string> = {
  tools: "tools",
  admin: "admin",
  news: "news",
  settings: "settings",
};

function crumbLabel(label: string): string {
  return formatBreadcrumbLabel(label);
}

function isCurrent(idx: number): boolean {
  return idx === props.segments.length - 1;
}

function crumbIconSlug(label: string): string | null {
  return CRUMB_ICONS[crumbLabel(label)] ?? null;
}

function currentClass(): string {
  if (props.elevated) {
    // Hierarchy via size/weight only — default text color, not accent gradient
    return "inline-flex h-10 items-center gap-2 truncate text-xl font-bold leading-none text-surface-light";
  }
  return "page-breadcrumb inline-flex items-center gap-2 font-medium text-surface-light";
}

const ancestorClass =
  "page-breadcrumb inline-flex items-center gap-2 text-surface-mid transition-colors hover:text-accent-blue";
</script>

<template>
  <nav aria-label="breadcrumb" class="page-breadcrumb min-w-0">
    <ol class="flex items-center gap-2">
      <li
        v-for="(seg, idx) in segments"
        :key="`${idx}:${seg.label}`"
        class="flex items-center gap-2"
      >
        <RouterLink
          v-if="seg.to"
          :to="seg.to"
          class="relative z-10 inline-flex h-10 cursor-pointer items-center"
          :aria-current="isCurrent(idx) ? 'page' : undefined"
        >
          <span :class="isCurrent(idx) ? currentClass() : ancestorClass">
            <ToolIcon
              v-if="crumbIconSlug(seg.label)"
              :slug="crumbIconSlug(seg.label)!"
              :class="isCurrent(idx) && elevated ? 'size-5 shrink-0' : 'size-3.5 shrink-0'"
            />
            {{ crumbLabel(seg.label) }}
          </span>
        </RouterLink>
        <span v-else :class="currentClass()" aria-current="page">
          <ToolIcon
            v-if="crumbIconSlug(seg.label)"
            :slug="crumbIconSlug(seg.label)!"
            :class="elevated ? 'size-5 shrink-0' : 'size-3.5 shrink-0'"
          />
          {{ crumbLabel(seg.label) }}
        </span>
        <span
          v-if="idx < segments.length - 1"
          class="page-breadcrumb inline-flex h-10 items-center text-surface-muted"
          aria-hidden="true"
          >/</span
        >
      </li>
    </ol>
  </nav>
</template>
