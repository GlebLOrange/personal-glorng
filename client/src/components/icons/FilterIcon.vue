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
    <path d="M4 5h16" />
    <path d="M7 12h10" />
    <path d="M10 19h4" />
  </svg>
</template>
