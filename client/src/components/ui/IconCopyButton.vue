<script setup lang="ts">
import CopyIcon from "@/components/icons/CopyIcon.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";

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
  <IconActionButton
    quiet
    :ariaLabel="ariaLabel"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <CopyIcon class-name="size-4" />
  </IconActionButton>
</template>
