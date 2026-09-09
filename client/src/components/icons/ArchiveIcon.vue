<script setup lang="ts">
withDefaults(
  defineProps<{
    /** Tailwind size class (default size-4). */
    className?: string;
    /** Use archive-restore glyph (unarchive). */
    restore?: boolean;
  }>(),
  {
    className: "size-4",
    restore: false,
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
    <rect width="20" height="5" x="2" y="3" rx="1" />
    <path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8" />
    <template v-if="restore">
      <path d="m9 15 3-3 3 3" />
      <path d="M12 12v9" />
    </template>
    <path v-else d="M10 12h4" />
  </svg>
</template>
