<script setup lang="ts">
import { computed, ref } from "vue";

const props = defineProps<{
  label: string;
  active?: boolean;
  colorClass?: string;
  disabled?: boolean;
}>();

const hovered = ref(false);

/** Status fill/text only — drop border-* so idle border chrome never fights colorClass. */
const statusFillClass = computed(() => {
  if (!props.colorClass) return "";
  return props.colorClass
    .split(/\s+/)
    .filter((token) => token && !token.startsWith("border-"))
    .join(" ");
});

const showStatusColor = computed(
  () => Boolean((props.active || hovered.value) && statusFillClass.value),
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
    class="w-full whitespace-nowrap rounded-lg border border-transparent px-2 py-1 text-left text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50 disabled:cursor-not-allowed disabled:opacity-50"
    :class="
      showStatusColor
        ? [statusFillClass, active ? 'ring-1 ring-inset ring-current/35' : undefined]
        : 'bg-transparent text-surface-mid'
    "
    @mouseenter="onEnter"
    @mouseleave="onLeave"
    @focus="onEnter"
    @blur="onLeave"
  >
    {{ label }}
  </button>
</template>
