<script setup lang="ts">
import PencilIcon from "@/components/icons/PencilIcon.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";

withDefaults(
  defineProps<{
    /** Accessible name for the icon-only control. */
    ariaLabel?: string;
    disabled?: boolean;
  }>(),
  {
    ariaLabel: "Edit",
  },
);

defineEmits<{ click: [MouseEvent] }>();
</script>

<template>
  <IconActionButton
    family="3xx"
    :ariaLabel="ariaLabel"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <PencilIcon class-name="size-4" />
  </IconActionButton>
</template>
