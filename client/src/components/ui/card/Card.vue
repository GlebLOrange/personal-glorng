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

const isNativeInteractive = computed(() => props.as === "button" || props.as === "a");

/** Non-native interactive cards need role/tabindex so focus rings activate. */
const needsKeyboardSemantics = computed(
  () => Boolean(props.interactive) && !isNativeInteractive.value,
);

const rootClass = computed(() => [
  "border rounded-lg",
  props.variant === "default" && "p-6 bg-surface-card border-surface-border",
  props.variant === "compact" && "p-4 bg-surface-card border-surface-border",
  props.variant === "dense" && "px-3 py-2 bg-surface-card border-surface-border rounded-lg",
  props.variant === "inset" && "p-3 bg-surface-dark/40 border-surface-border",
  props.variant === "ghost" && "p-0 bg-transparent border-transparent",
  props.tint === "danger" && "border-status-error/60 bg-status-error/10",
  props.hoverable &&
    "hover:border-accent-blue active:border-accent-blue/80 transition-colors duration-200",
  props.interactive &&
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 transition-colors duration-200",
  attrs.class,
]);

const rootAttrs = computed(() => {
  const { class: _class, ...rest } = attrs as Record<string, unknown>;
  void _class;
  if (!needsKeyboardSemantics.value) {
    if (props.as === "button" && rest.type == null) {
      return { ...rest, type: "button" };
    }
    return rest;
  }
  return {
    ...rest,
    role: typeof rest.role === "string" ? rest.role : "button",
    tabindex: rest.tabindex != null ? rest.tabindex : 0,
  };
});

function onKeydown(event: KeyboardEvent): void {
  if (!needsKeyboardSemantics.value) return;
  if (event.key !== "Enter" && event.key !== " ") return;
  event.preventDefault();
  (event.currentTarget as HTMLElement).click();
}
</script>

<template>
  <component :is="as" v-bind="rootAttrs" :class="rootClass" @keydown="onKeydown">
    <slot />
  </component>
</template>
