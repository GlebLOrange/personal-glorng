<script setup lang="ts">
import IconActionButton from "@/components/ui/IconActionButton.vue";

withDefaults(
  defineProps<{
    /** Accessible name for the icon-only control. */
    ariaLabel?: string;
    disabled?: boolean;
  }>(),
  {
    ariaLabel: "Close",
  },
);

defineEmits<{ click: [MouseEvent] }>();
</script>

<template>
  <IconActionButton
    danger
    :ariaLabel="ariaLabel"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    ✕
  </IconActionButton>
</template>
