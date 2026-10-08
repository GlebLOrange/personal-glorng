<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";

import ToolIcon from "@/components/icons/ToolIcon.vue";
import { Card } from "@/components/ui/card";
import { tileHintForSlug } from "@/constants/toolIntros";
import type { PlatformService } from "@/platform/services";

export type ToolTileSection = {
  category: string;
  label: string;
  services: PlatformService[];
};

const props = withDefaults(
  defineProps<{
    sections: ToolTileSection[];
    /** Resolve in-app route for a service (Tools page). Ignored when service.external. */
    resolveRoute?: (tool: PlatformService) => string;
    gapClass?: string;
    /** When false, hide per-section h2 (e.g. category already shown in tabs). */
    showCategoryHeadings?: boolean;
    /** Use h3 when this grid sits under a parent section heading (e.g. “your tools”). */
    categoryHeading?: "h2" | "h3";
    /** Compact rhythm for ops hubs (admin); default keeps airier tools layout. */
    density?: "default" | "compact";
  }>(),
  {
    showCategoryHeadings: true,
    categoryHeading: "h2",
    density: "default",
  },
);

const sectionClass = computed(() =>
  props.showCategoryHeadings ? (props.density === "compact" ? "mb-6" : "mb-8") : "mb-0",
);

const headingClass = computed(() =>
  props.density === "compact"
    ? "text-meta mb-2 uppercase tracking-wider"
    : "text-meta mb-3 uppercase tracking-wider",
);

const tileTitleTag = computed(() => (props.categoryHeading === "h3" ? "h4" : "h3"));

const iconChipClass = computed(() => (props.density === "compact" ? "h-9 w-9" : "h-10 w-10"));

function tileTo(tool: PlatformService): string {
  return props.resolveRoute ? props.resolveRoute(tool) : tool.adminRoute;
}

function tileLinkAttrs(
  tool: PlatformService,
): { href: string; target: string; rel: string } | { to: string } {
  if (tool.external) {
    return {
      href: tool.adminRoute,
      target: "_blank",
      rel: "noopener noreferrer",
    };
  }
  return { to: tileTo(tool) };
}

function toolCountLabel(count: number): string {
  return count === 1 ? "1 tool" : `${count} tools`;
}

/** Nested under a parent heading (e.g. “your tools”) — skip a lonely category label. */
function showSectionHeading(section: ToolTileSection): boolean {
  if (!props.showCategoryHeadings) return false;
  if (props.categoryHeading === "h3" && section.services.length === 1) return false;
  return true;
}

function tileHint(tool: PlatformService): string | undefined {
  return tileHintForSlug(tool.slug);
}
</script>

<template>
  <section
    v-for="section in sections"
    :key="section.category"
    class="min-w-0"
    :class="sectionClass"
  >
    <component :is="categoryHeading" v-if="showSectionHeading(section)" :class="headingClass">
      {{ section.label }}
      <span class="sr-only">, {{ toolCountLabel(section.services.length) }}</span>
      <span
        aria-hidden="true"
        class="ml-2 font-normal tracking-normal text-surface-mid normal-case"
      >
        {{ section.services.length }}
      </span>
    </component>
    <div class="page-launcher-grid" :class="gapClass" :data-density="density">
      <component
        :is="tool.external ? 'a' : RouterLink"
        v-for="tool in section.services"
        :key="tool.slug"
        class="page-tile group"
        v-bind="tileLinkAttrs(tool)"
      >
        <Card hoverable class="page-tile-card h-full w-full">
          <span
            class="grid shrink-0 place-items-center rounded-lg bg-surface-grid text-surface-light"
            :class="iconChipClass"
            aria-hidden="true"
          >
            <ToolIcon :slug="tool.slug" class="h-5 w-5" />
          </span>
          <span class="min-w-0 flex-1">
            <component
              :is="tileTitleTag"
              class="text-sm font-semibold leading-snug break-words text-surface-light"
            >
              {{ tool.name }}
              <span v-if="tool.external" class="font-normal text-surface-mid" aria-hidden="true">
                ↗
              </span>
            </component>
            <p
              v-if="tileHint(tool)"
              class="mt-0.5 line-clamp-2 text-xs leading-snug break-words text-surface-mid"
            >
              {{ tileHint(tool) }}
            </p>
            <span v-if="tool.external" class="sr-only">opens in a new tab</span>
          </span>
          <svg
            class="page-tile-chevron h-4 w-4 shrink-0 text-surface-mid transition-transform duration-200 group-hover:translate-x-0.5 group-hover:text-surface-light group-focus-visible:translate-x-0.5 group-focus-visible:text-surface-light"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path d="m9 6 6 6-6 6" />
          </svg>
        </Card>
      </component>
    </div>
  </section>
</template>
