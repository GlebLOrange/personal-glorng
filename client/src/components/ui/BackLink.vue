<script setup lang="ts">
import { computed, useAttrs } from "vue";
import type { RouteLocationRaw } from "vue-router";

import { actionFamilyClass } from "@/constants/httpStatusColors";

defineOptions({ inheritAttrs: false });

const props = withDefaults(
  defineProps<{
    to: RouteLocationRaw;
    size?: "default" | "compact";
  }>(),
  {
    size: "default",
  },
);

const attrs = useAttrs();

const sizeClass = computed(() =>
  props.size === "compact"
    ? "!min-h-8 !min-w-8 !h-8 !w-8"
    : "!min-h-11 !min-w-11 !h-11 !w-11",
);

const iconClass = computed(() => (props.size === "compact" ? "size-4" : "size-5"));

function linkClass(isActive: boolean): string {
  return [
    actionFamilyClass("1xx", isActive),
    // Borderless icon control; anchors ignore :enabled so mirror 1xx hover without it.
    "!border-transparent hover:!border-transparent focus-visible:!border-transparent !px-0",
    isActive ? "" : "hover:text-accent-blue hover:bg-accent-blue/15",
    sizeClass.value,
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
        :class="iconClass"
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
