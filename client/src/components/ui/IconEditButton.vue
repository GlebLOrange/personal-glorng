<script setup lang="ts">
import PencilIcon from "@/components/icons/PencilIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";

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
  <BaseButton
    variant="ghost"
    size="icon"
    class="!bg-accent-golden/3 !text-accent-golden hover:enabled:!border-accent-golden/40 hover:enabled:!bg-accent-golden/15 focus-visible:!text-accent-golden"
    :aria-label="ariaLabel"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <PencilIcon class-name="size-4" />
  </BaseButton>
</template>
