<script setup lang="ts">
import { computed, useAttrs } from "vue";

defineOptions({ inheritAttrs: false });

const props = withDefaults(
  defineProps<{
    variant?: "default" | "compact" | "dense" | "inset" | "ghost";
    tint?: "default" | "danger";
    hoverable?: boolean;
    interactive?: boolean;
    as?: "div" | "section" | "article" | "button" | "a" | "li" | "footer" | "header";
  }>(),
  {
    variant: "default",
    tint: "default",
    as: "div",
  },
);

const attrs = useAttrs();

const rootClass = computed(() => [
  "border rounded-lg",
  props.variant === "default" && "p-6 bg-surface-card border-surface-border",
  props.variant === "compact" && "p-4 bg-surface-card border-surface-border",
  props.variant === "dense" && "px-3 py-2 bg-surface-card border-surface-border rounded-lg",
  props.variant === "inset" && "p-3 bg-surface-dark/40 border-surface-border",
  props.variant === "ghost" && "p-0 bg-transparent border-transparent",
  props.tint === "danger" && "border-status-error/60 bg-status-error/10",
  props.hoverable && "hover:border-accent-blue active:border-accent-blue/80 transition-colors duration-200",
  props.interactive &&
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 transition-colors duration-200",
  attrs.class,
]);
</script>

<template>
  <component :is="as" v-bind="{ ...attrs, class: undefined }" :class="rootClass">
    <slot />
  </component>
</template>
