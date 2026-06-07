<script setup lang="ts">
defineProps<{
  tag: string;
  active?: boolean;
  compact?: boolean;
}>();

const emit = defineEmits<{
  click: [];
}>();
</script>

<template>
  <button
    type="button"
    :class="[
      'shrink-0 rounded-full border transition-colors',
      compact ? 'text-[10px] px-2 py-0.5' : 'text-xs px-3 py-1',
      active
        ? 'border-accent-blue bg-accent-blue/15 text-accent-blue'
        : 'border-accent-blue/40 text-accent-blue hover:bg-accent-blue/10',
    ]"
    @click.stop="emit('click')"
  >
    {{ tag }}
  </button>
</template>
