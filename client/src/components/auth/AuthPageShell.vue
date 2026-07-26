<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";

const props = withDefaults(
  defineProps<{
    title: string;
    /** login: left title + absolute BackLink + vertical offset; centered: default auth pages */
    variant?: "centered" | "login";
    maxWidth?: "sm" | "md";
    backTo?: RouteLocationRaw;
    titleAlign?: "left" | "center";
  }>(),
  {
    variant: "centered",
    maxWidth: "sm",
    backTo: undefined,
    titleAlign: undefined,
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

const resolvedTitleAlign = computed(
  () => props.titleAlign ?? (props.variant === "login" ? "left" : "center"),
);

const titleClass = computed(() => [
  "text-2xl font-bold text-surface-light",
  props.variant === "login" ? "pr-14 mb-0 text-left min-h-11" : "mb-8",
  resolvedTitleAlign.value === "center" ? "text-center" : "text-left",
]);
</script>

<template>
  <div :class="outerClass">
    <div :class="innerClass">
      <div v-if="title" :class="variant === 'login' ? 'relative mb-8 min-h-11' : undefined">
        <h1 :class="titleClass">
          <span class="accent-gradient">{{ title }}</span>
        </h1>
        <BackLink
          v-if="backTo && variant === 'login'"
          :to="backTo"
          class="absolute right-0 top-0"
        />
      </div>
      <slot />
      <p v-if="backTo && variant === 'centered'" class="flex justify-center mt-6">
        <BackLink :to="backTo" />
      </p>
    </div>
  </div>
</template>
