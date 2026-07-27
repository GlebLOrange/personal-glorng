<script setup lang="ts">
import PencilIcon from "@/components/icons/PencilIcon.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";

withDefaults(
  defineProps<{
    /** Accessible name for the icon-only control. */
    ariaLabel?: string;
    disabled?: boolean;
    /** field = in-shell clear (fills parent shell height); default = CONTROL_SIZE square (h-10). */
    size?: "md" | "field";
  }>(),
  {
    ariaLabel: "Edit",
    size: "md",
  },
);

defineEmits<{ click: [MouseEvent] }>();
</script>

<template>
  <IconActionButton
    family="3xx"
    :size="size"
    :aria-label="ariaLabel"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <PencilIcon class-name="size-4" />
  </IconActionButton>
</template>
