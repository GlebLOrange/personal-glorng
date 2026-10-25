<script setup lang="ts">
import { computed } from "vue";
import { RouterLink } from "vue-router";

import ToolIcon from "@/components/icons/ToolIcon.vue";
import { Card } from "@/components/ui/card";
import { publicTileBlurbForSlug, tileHintForSlug } from "@/constants/toolIntros";
import { ADMIN_HUB_DEMO_SLUGS, type PlatformService } from "@/platform/services";

export type ToolTileSection = {
  category: string;
  label: string;
  services: PlatformService[];
};

export type ToolTileChip = "demo" | "yours";

const props = withDefaults(
  defineProps<{
    sections: ToolTileSection[];
    /** Resolve in-app route for a service (Tools page). Ignored when service.external. */
    resolveRoute?: (tool: PlatformService) => string;
    gapClass?: string;
    /** When false, hide per-section category headings. */
    showCategoryHeadings?: boolean;
    /** Use h3 when this grid sits under a parent section heading (e.g. “your tools”). */
    categoryHeading?: "h2" | "h3";
    /** Compact rhythm for ops hubs (admin); default keeps airier tools layout. */
    density?: "default" | "compact";
    /**
     * `public` — guest Tools catalog: larger touch targets, every-tile blurbs,
     * sentence-case "Label · N" counts.
     * `admin` — /admin hub: same heading pattern, one-line descriptions, demo chips.
     * Default keeps signed-in tile behavior (same heading + count).
     */
    presentation?: "default" | "public" | "admin";
    /** Optional per-slug chip (demo / yours). Admin omits this. */
    tileChip?: (slug: string) => ToolTileChip | undefined;
  }>(),
  {
    showCategoryHeadings: true,
    categoryHeading: "h2",
    density: "default",
    presentation: "default",
  },
);

const isPublicPresentation = computed(() => props.presentation === "public");
const isAdminPresentation = computed(() => props.presentation === "admin");

const sectionClass = computed(() =>
  props.showCategoryHeadings ? (props.density === "compact" ? "mb-6" : "mb-8") : "mb-0",
);

const headingClass = computed(() =>
  props.density === "compact"
    ? "mb-2 text-sm font-semibold text-surface-light"
    : "mb-3 text-sm font-semibold text-surface-light",
);

const tileTitleTag = computed(() => (props.categoryHeading === "h3" ? "h4" : "h3"));

const iconChipClass = computed(() => {
  if (isPublicPresentation.value) return "h-11 w-11";
  return props.density === "compact" ? "h-9 w-9" : "h-10 w-10";
});

function tileTo(tool: PlatformService): string {
  if (isAdminPresentation.value) return tool.adminRoute;
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
  if (isAdminPresentation.value) return true;
  if (props.categoryHeading === "h3" && section.services.length === 1) return false;
  return true;
}

function tileHint(tool: PlatformService): string | undefined {
  if (isPublicPresentation.value) {
    return publicTileBlurbForSlug(tool.slug);
  }
  return tileHintForSlug(tool.slug);
}

function chipFor(tool: PlatformService): ToolTileChip | undefined {
  if (isAdminPresentation.value) return undefined;
  return props.tileChip?.(tool.slug);
}

function showAdminDemoChip(tool: PlatformService): boolean {
  return isAdminPresentation.value && ADMIN_HUB_DEMO_SLUGS.has(tool.slug);
}
</script>

<template>
  <section
    v-for="section in sections"
    :id="section.category"
    :key="section.category"
    class="min-w-0"
    :class="sectionClass"
  >
    <component :is="categoryHeading" v-if="showSectionHeading(section)" :class="headingClass">
      <span aria-hidden="true">{{ `${section.label} · ${section.services.length}` }}</span>
      <span class="sr-only">{{ section.label }}, {{ toolCountLabel(section.services.length) }}</span>
    </component>
    <div
      class="page-launcher-grid"
      :class="gapClass"
      :data-density="density"
      :data-presentation="presentation"
    >
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
            <span class="flex min-w-0 flex-wrap items-center gap-2">
              <component
                :is="tileTitleTag"
                class="text-sm font-semibold leading-snug break-words text-surface-light"
              >
                {{ tool.name }}
                <span v-if="tool.external" class="font-normal text-surface-mid" aria-hidden="true">
                  ↗
                </span>
              </component>
              <span
                v-if="showAdminDemoChip(tool)"
                class="shrink-0 rounded border border-transparent bg-surface-grid px-1.5 py-0.5 text-xs font-medium text-surface-sage"
              >
                Demo
              </span>
              <span
                v-else-if="chipFor(tool)"
                class="shrink-0 rounded border border-transparent bg-surface-grid px-1.5 py-0.5 text-xs font-medium text-surface-mid"
              >
                {{ chipFor(tool) }}
              </span>
            </span>
            <p
              v-if="isAdminPresentation"
              class="mt-0.5 line-clamp-1 text-xs leading-snug break-words text-surface-mid"
            >
              {{ tool.description }}
            </p>
            <p
              v-else-if="tileHint(tool)"
              class="mt-0.5 text-xs leading-snug break-words text-surface-mid"
              :class="isPublicPresentation ? '' : 'line-clamp-2'"
            >
              {{ tileHint(tool) }}
            </p>
            <span v-if="tool.external" class="sr-only">opens in a new tab</span>
          </span>
          <svg
            class="page-tile-chevron pointer-events-none h-4 w-4 shrink-0 text-surface-mid transition-transform duration-200 group-hover:translate-x-0.5 group-hover:text-surface-light group-focus-visible:translate-x-0.5 group-focus-visible:text-surface-light"
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
