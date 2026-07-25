<script setup lang="ts">
import CopyIcon from "@/components/icons/CopyIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";

withDefaults(
  defineProps<{
    /** Accessible name for the icon-only control. */
    ariaLabel?: string;
    disabled?: boolean;
  }>(),
  {
    ariaLabel: "copy",
  },
);

defineEmits<{ click: [MouseEvent] }>();
</script>

<template>
  <BaseButton
    variant="ghost"
    quiet
    size="icon"
    :aria-label="ariaLabel"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <CopyIcon class-name="size-4" />
  </BaseButton>
</template>
