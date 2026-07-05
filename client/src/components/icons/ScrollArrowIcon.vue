<script setup lang="ts">
defineProps<{
  direction: "up" | "down";
}>();
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
    class="size-5"
  >
    <path v-if="direction === 'down'" d="M12 5v14M5 12l7 7 7-7" />
    <path v-else d="M12 19V5M5 12l7-7 7 7" />
  </svg>
</template>
