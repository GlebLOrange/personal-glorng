<script setup lang="ts">
import CopyIcon from "@/components/icons/CopyIcon.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";

withDefaults(
  defineProps<{
    /** Accessible name for the icon-only control. */
    ariaLabel?: string;
    disabled?: boolean;
    /** field = in-shell (same h-10 square); default chrome (h-10). */
    size?: "md" | "field";
    /** Muted until hover; set false to match ghost 1xx wash (e.g. beside show). */
    quiet?: boolean;
  }>(),
  {
    ariaLabel: "copy",
    size: "md",
    quiet: true,
  },
);

defineEmits<{ click: [MouseEvent] }>();
</script>

<template>
  <IconActionButton
    :quiet="quiet"
    family="1xx"
    :size="size"
    :aria-label="ariaLabel"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <CopyIcon class-name="size-4" />
  </IconActionButton>
</template>
