<script setup lang="ts">
import { computed, ref } from "vue";

import { FILTER_MENU_ROW_CLASS } from "@/constants/toolbarPopover";

const props = withDefaults(
  defineProps<{
    label: string;
    active?: boolean;
    colorClass?: string;
    disabled?: boolean;
    /** Filters menus stay left; status bars can center. */
    align?: "left" | "center";
  }>(),
  {
    align: "left",
  },
);

const hovered = ref(false);

const showStatusColor = computed(() =>
  Boolean((props.active || hovered.value) && props.colorClass),
);

const alignClass = computed(() =>
  props.align === "center" ? "justify-center text-center" : "justify-start text-left",
);

function onEnter(): void {
  if (!props.disabled) hovered.value = true;
}

function onLeave(): void {
  hovered.value = false;
}
</script>

<template>
  <button
    type="button"
    :disabled="disabled"
    :aria-pressed="active"
    :class="[
      FILTER_MENU_ROW_CLASS,
      alignClass,
      showStatusColor
        ? [colorClass, active ? 'ring-1 ring-inset ring-current/35' : undefined]
        : 'border-transparent bg-transparent text-surface-mid hover:border-surface-border/50',
    ]"
    @mouseenter="onEnter"
    @mouseleave="onLeave"
    @focus="onEnter"
    @blur="onLeave"
  >
    {{ label }}
  </button>
</template>
