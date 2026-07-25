<script setup lang="ts">
withDefaults(
  defineProps<{
    /** Tailwind size class (default size-4). */
    className?: string;
  }>(),
  {
    className: "size-4",
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
    <circle cx="11" cy="11" r="6" />
    <path d="m20 20-3.5-3.5" />
  </svg>
</template>
