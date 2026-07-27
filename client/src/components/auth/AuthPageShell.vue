<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";

const props = withDefaults(
  defineProps<{
    title: string;
    /** login: vertical offset in the viewport; centered: default auth pages */
    variant?: "centered" | "login";
    maxWidth?: "sm" | "md";
    backTo?: RouteLocationRaw;
    /** Title alignment — left by default (matches login). */
    titleAlign?: "left" | "center";
  }>(),
  {
    variant: "centered",
    maxWidth: "sm",
    backTo: undefined,
    titleAlign: "left",
  },
);

const outerClass = computed(() =>
  props.variant === "login"
    ? "flex min-h-[calc(100dvh-8rem)] items-center justify-center px-6 py-12"
    : "min-h-[80vh] flex items-center justify-center px-6",
);

const innerClass = computed(() => [
  "w-full",
  props.maxWidth === "md" ? "max-w-md" : "max-w-sm",
  props.variant === "login" ? "relative -translate-y-[15dvh]" : undefined,
]);

const showHeaderBack = computed(() => Boolean(props.backTo && props.title));

const titleClass = computed(() => [
  "text-2xl font-bold leading-none text-surface-light",
  showHeaderBack.value ? "pr-14" : undefined,
  props.titleAlign === "center" ? "text-center" : "text-left",
]);
</script>

<template>
  <div :class="outerClass">
    <div :class="innerClass">
      <div class="space-y-4">
        <div v-if="title" class="relative flex h-10 items-center">
          <h1 :class="titleClass">
            <span class="accent-gradient">{{ title }}</span>
          </h1>
          <BackLink
            v-if="showHeaderBack"
            :to="backTo!"
            class="absolute right-0 top-1/2 -translate-y-1/2"
          />
        </div>
        <slot />
      </div>
      <p v-if="backTo && !title" class="mt-6 flex justify-center">
        <BackLink :to="backTo" />
      </p>
    </div>
  </div>
</template>
