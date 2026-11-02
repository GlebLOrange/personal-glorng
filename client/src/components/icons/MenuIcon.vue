<script setup lang="ts">
withDefaults(
  defineProps<{
    /** Tailwind size class (default size-3.5). */
    className?: string;
    /** When true, render an X instead of hamburger lines. */
    open?: boolean;
  }>(),
  {
    className: "size-3.5",
    open: false,
  },
);
</script>

<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    :class="className"
  >
    <path v-if="!open" d="M4 7h16M4 12h16M4 17h16" />
    <path v-else d="M6 6l12 12M18 6 6 18" />
  </svg>
</template>
