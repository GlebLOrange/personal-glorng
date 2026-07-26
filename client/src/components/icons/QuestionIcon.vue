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
    <circle cx="12" cy="12" r="9" />
    <path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 2.5-3 4.5" />
    <path d="M12 17h.01" />
  </svg>
</template>
