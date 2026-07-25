<script setup lang="ts">
withDefaults(
  defineProps<{
    tag: string;
    active?: boolean;
    compact?: boolean;
    /** When false, render a non-interactive span (safe inside a parent button). */
    interactive?: boolean;
  }>(),
  {
    interactive: true,
  },
);

const emit = defineEmits<{
  click: [];
}>();
</script>

<template>
  <component
    :is="interactive ? 'button' : 'span'"
    :type="interactive ? 'button' : undefined"
    :aria-pressed="interactive ? Boolean(active) : undefined"
    :class="[
      'rounded-full border transition-colors',
      compact ? 'min-h-0 text-[10px] px-2 py-0.5' : 'min-h-9 text-xs px-2 py-1',
      active
        ? 'border-accent-blue bg-accent-blue/15 text-accent-blue'
        : 'border-accent-blue/40 text-accent-blue',
      interactive && !active ? 'hover:bg-accent-blue/10' : undefined,
    ]"
    @click.stop="interactive ? emit('click') : undefined"
  >
    {{ tag }}
  </component>
</template>
