<script setup lang="ts">
import { computed, useAttrs } from "vue";
import type { RouteLocationRaw } from "vue-router";

import { actionFamilyClass } from "@/constants/httpStatusColors";

defineOptions({ inheritAttrs: false });

withDefaults(
  defineProps<{
    to: RouteLocationRaw;
    /** @deprecated Alias of default — both sizes match BaseButton icon hit target. */
    size?: "default" | "compact";
  }>(),
  {
    size: "default",
  },
);

const attrs = useAttrs();

/** Match BaseButton size="icon" / IconCloseButton. */
const sizeClass = "!min-h-8 !min-w-8 !h-8 !w-8 !px-0";

function linkClass(isActive: boolean): string {
  return [
    actionFamilyClass("1xx", isActive),
    // Anchors ignore :enabled — mirror 1xx hover border/bg without it.
    "hover:border-accent-blue/40 focus-visible:border-accent-blue/40",
    isActive ? "" : "hover:text-accent-blue hover:bg-accent-blue/15",
    sizeClass,
    attrs.class,
  ]
    .filter(Boolean)
    .join(" ");
}

const nativeAttrs = computed(() => {
  const next: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(attrs)) {
    if (key !== "class" && key !== "style") next[key] = value;
  }
  return next;
});
</script>

<template>
  <RouterLink v-slot="{ href, navigate, isActive }" :to="to" custom>
    <a
      :href="href"
      aria-label="Back"
      :class="linkClass(isActive)"
      :style="attrs.style"
      v-bind="nativeAttrs"
      @click="navigate($event)"
    >
      <svg
        class="size-4"
        viewBox="0 0 40 40"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M24 11 15 20l9 9" />
        <path d="M16 20h18" />
      </svg>
    </a>
  </RouterLink>
</template>
