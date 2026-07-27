<script setup lang="ts">
import { computed } from "vue";

import ToolIcon from "@/components/icons/ToolIcon.vue";
import { Card } from "@/components/ui/card";
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
    /** Compact rhythm for ops hubs (admin); default keeps airier tools layout. */
    density?: "default" | "compact";
  }>(),
  {
    showCategoryHeadings: true,
    density: "default",
  },
);

const sectionClass = computed(() =>
  props.showCategoryHeadings
    ? props.density === "compact"
      ? "mb-8"
      : "mb-10"
    : "mb-0",
);

const headingClass = computed(() =>
  props.density === "compact" ? "text-meta mb-3 uppercase tracking-wider" : "text-meta mb-4 uppercase tracking-wider",
);
</script>

<template>
  <section
    v-for="section in sections"
    :key="section.category"
    class="min-w-0"
    :class="sectionClass"
  >
    <h2 v-if="showCategoryHeadings" :class="headingClass">
      {{ section.label }}
    </h2>
    <div class="page-tool-grid" :class="gapClass">
      <template v-for="tool in section.services" :key="tool.slug">
        <a
          v-if="tool.external"
          class="page-tile"
          :href="tool.adminRoute"
          target="_blank"
          rel="noopener noreferrer"
          :aria-label="`${tool.name} (opens in new tab)`"
        >
          <Card hoverable class="page-tile-card h-full">
            <div class="flex min-w-0 items-center gap-2">
              <ToolIcon :slug="tool.slug" class="h-6 w-6 shrink-0 text-surface-light" />
              <h3 class="min-w-0 text-sm font-semibold text-surface-light break-words">
                {{ tool.name }}
                <span class="text-surface-mid font-normal" aria-hidden="true"> ↗</span>
              </h3>
            </div>
            <p class="line-clamp-3 text-xs lowercase leading-relaxed text-surface-mid break-words">
              {{ tool.description }}
            </p>
          </Card>
        </a>
        <RouterLink
          v-else
          class="page-tile"
          :to="resolveRoute ? resolveRoute(tool) : tool.adminRoute"
        >
          <Card hoverable class="page-tile-card h-full">
            <div class="flex min-w-0 items-center gap-2">
              <ToolIcon :slug="tool.slug" class="h-6 w-6 shrink-0 text-surface-light" />
              <h3 class="min-w-0 text-sm font-semibold text-surface-light break-words">
                {{ tool.name }}
              </h3>
            </div>
            <p class="line-clamp-3 text-xs lowercase leading-relaxed text-surface-mid break-words">
              {{ tool.description }}
            </p>
          </Card>
        </RouterLink>
      </template>
    </div>
  </section>
</template>
