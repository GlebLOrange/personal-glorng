<script setup lang="ts">
withDefaults(
  defineProps<{
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
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    :class="className"
  >
    <path d="M21 12a9 9 0 0 0-15.5-6.4" />
    <path d="M5.5 5.6V9h3.4" />
    <path d="M3 12a9 9 0 0 0 15.5 6.4" />
    <path d="M18.5 18.4V15h-3.4" />
  </svg>
</template>
