<script setup lang="ts">
/**
 * Period-hinge GY mark for chrome (nav/footer).
 * Ink follows currentColor; period uses the theme accent token.
 */
withDefaults(
  defineProps<{
    /** Tailwind size classes (default h-7 w-7). */
    className?: string;
  }>(),
  {
    className: "h-7 w-7",
  },
);
</script>

<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 64 64"
    fill="none"
    aria-hidden="true"
    :class="className"
  >
    <path
      fill="currentColor"
      d="M41.28 14.38A23.00 23.00 0 1 0 41.28 49.62L35.18 42.34A13.50 13.50 0 1 1 35.18 21.66Z"
    />
    <path
      fill="currentColor"
      d="M45.15 30.54L37.65 19.54L33.35 22.46L40.85 33.46ZM44.87 33.81L59.87 18.31L56.13 14.69L41.13 30.19ZM40.40 32.00L40.40 53.50L45.60 53.50L45.60 32.00Z"
    />
    <circle cx="43" cy="32" r="3.8" fill="var(--color-accent-blue)" />
  </svg>
</template>
