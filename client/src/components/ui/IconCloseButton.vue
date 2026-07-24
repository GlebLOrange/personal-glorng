<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";

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
  <BaseButton
    variant="ghost"
    danger
    size="sm"
    class="!h-8 !w-8 !min-w-8 px-0"
    :aria-label="ariaLabel"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    ✕
  </BaseButton>
</template>
