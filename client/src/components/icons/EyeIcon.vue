<script setup lang="ts">
withDefaults(
  defineProps<{
    /** Tailwind size class (default size-4). */
    className?: string;
    /** Crossed-out eye when the value is visible (hide action). */
    off?: boolean;
  }>(),
  {
    className: "size-4",
    off: false,
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
    <template v-if="off">
      <path d="M10.733 5.076a10.641 10.641 0 0 1 11.16 6.198 10.66 10.66 0 0 1-1.402 2.55" />
      <path d="M14.084 14.158a3 3 0 0 1-4.242-4.242" />
      <path d="M17.479 17.499a10.64 10.64 0 0 1-15.372-6.225 10.66 10.66 0 0 1 3.05-4.05" />
      <path d="M2 2l20 20" />
    </template>
    <template v-else>
      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </template>
  </svg>
</template>
