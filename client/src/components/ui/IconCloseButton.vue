<script setup lang="ts">
import IconActionButton from "@/components/ui/IconActionButton.vue";

withDefaults(
  defineProps<{
    /** Accessible name for the icon-only control. */
    ariaLabel?: string;
    disabled?: boolean;
    /** field = in-shell clear (same h-10 square); default header/chrome (h-10). */
    size?: "md" | "field";
  }>(),
  {
    ariaLabel: "close",
    size: "md",
  },
);

defineEmits<{ click: [MouseEvent] }>();
</script>

<template>
  <IconActionButton
    danger
    :size="size"
    :aria-label="ariaLabel"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <!-- SVG so the glyph centers optically (✕ text sits high in the em box) -->
    <svg class="size-3.5 shrink-0" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path
        d="M3.5 3.5l7 7m0-7l-7 7"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
      />
    </svg>
  </IconActionButton>
</template>
