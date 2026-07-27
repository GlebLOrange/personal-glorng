<script setup lang="ts">
import { computed, useAttrs } from "vue";
import type { RouteLocationRaw } from "vue-router";

import ScrollArrowIcon from "@/components/icons/ScrollArrowIcon.vue";
import { iconActionClass } from "@/constants/httpStatusColors";

defineOptions({ inheritAttrs: false });

withDefaults(
  defineProps<{
    to: RouteLocationRaw;
    /** @deprecated Alias of default — both sizes match IconActionButton. */
    size?: "default" | "compact";
  }>(),
  {
    size: "default",
  },
);

const attrs = useAttrs();

function linkClass(isActive: boolean): string {
  return [iconActionClass("1xx", isActive, { anchor: true }), attrs.class]
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
      aria-label="back"
      :class="linkClass(isActive)"
      :style="attrs.style"
      v-bind="nativeAttrs"
      @click="navigate($event)"
    >
      <ScrollArrowIcon direction="left" />
    </a>
  </RouterLink>
</template>
