<script setup lang="ts">
defineProps<{
  destructive?: boolean;
}>();

const emit = defineEmits<{
  select: [];
}>();

function onClick(): void {
  emit("select");
}
</script>

<template>
  <button
    type="button"
    role="menuitem"
    :class="[
      'w-full text-left px-3 py-2 text-sm transition-colors',
      destructive
        ? 'text-red-400 hover:bg-red-400/10'
        : 'text-surface-light hover:bg-surface-border/40',
    ]"
    @click="onClick"
  >
    <slot />
  </button>
</template>
