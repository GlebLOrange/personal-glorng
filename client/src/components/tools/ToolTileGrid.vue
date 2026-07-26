<script setup lang="ts">
import ToolIcon from "@/components/icons/ToolIcon.vue";
import { Card } from "@/components/ui/card";
import type { PlatformService } from "@/platform/services";

export type ToolTileSection = {
  category: string;
  label: string;
  services: PlatformService[];
};

defineProps<{
  sections: ToolTileSection[];
  /** Resolve in-app route for a service (Tools page). Ignored when service.external. */
  resolveRoute?: (tool: PlatformService) => string;
  gapClass?: string;
}>();
</script>

<template>
  <section v-for="section in sections" :key="section.category" class="mb-10 min-w-0">
    <h2 class="text-meta mb-4 uppercase tracking-wider">{{ section.label }}</h2>
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
            <ToolIcon :slug="tool.slug" class="mb-3 h-8 w-8 text-surface-light" />
            <h3 class="text-surface-light font-bold mb-1 break-words">
              {{ tool.name }}
              <span class="text-surface-mid font-normal"> ↗</span>
            </h3>
            <p class="text-xs text-surface-mid break-words">{{ tool.description }}</p>
          </Card>
        </a>
        <RouterLink
          v-else
          class="page-tile"
          :to="resolveRoute ? resolveRoute(tool) : tool.adminRoute"
        >
          <Card hoverable class="page-tile-card h-full">
            <ToolIcon :slug="tool.slug" class="mb-3 h-8 w-8 text-surface-light" />
            <h3 class="text-surface-light font-bold mb-1 break-words">{{ tool.name }}</h3>
            <p class="text-xs text-surface-mid break-words">{{ tool.description }}</p>
          </Card>
        </RouterLink>
      </template>
    </div>
  </section>
</template>
