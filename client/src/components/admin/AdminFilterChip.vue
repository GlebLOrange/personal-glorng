<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  label: string;
  active?: boolean;
  colorClass?: string;
  disabled?: boolean;
}>();

const hovered = ref(false);

const showStatusColor = computed(() =>
  Boolean((props.active || hovered.value) && props.colorClass),
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
    class="w-full whitespace-nowrap rounded-lg border px-2 py-1 text-left text-xs leading-normal transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 disabled:cursor-not-allowed disabled:opacity-50"
    :class="
      showStatusColor
        ? [colorClass, active ? 'ring-1 ring-inset ring-current/35' : undefined]
        : 'border-transparent bg-transparent text-surface-mid hover:border-surface-border/50'
    "
    @mouseenter="onEnter"
    @mouseleave="onLeave"
    @focus="onEnter"
    @blur="onLeave"
  >
    {{ label }}
  </button>
</template>
