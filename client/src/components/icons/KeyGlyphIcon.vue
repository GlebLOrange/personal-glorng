<script setup lang="ts">
withDefaults(
  defineProps<{
    /** Single character shown as the glyph (digits / operators). */
    glyph: string;
    /** Tailwind size class (default size-3.5). */
    className?: string;
  }>(),
  {
    className: "size-3.5",
  },
);
</script>

<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="currentColor"
    aria-hidden="true"
    :class="className"
  >
    <text
      x="12"
      y="16.5"
      text-anchor="middle"
      font-size="14"
      font-weight="600"
      font-family="ui-sans-serif, system-ui, sans-serif"
    >
      {{ glyph }}
    </text>
  </svg>
</template>
