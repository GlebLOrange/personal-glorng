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
    <path d="M4 6h16v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6Z" />
    <path d="M4 6 8 2h8l4 4" />
    <path d="M12 11v5M9.5 13.5 12 11l2.5 2.5" />
  </svg>
</template>
