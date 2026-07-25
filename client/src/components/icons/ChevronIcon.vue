<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    /** Points down when closed; flips when open. */
    open?: boolean;
    className?: string;
  }>(),
  {
    open: false,
    className: "size-3.5",
  },
);

const rotateClass = computed(() => (props.open ? "rotate-180" : "rotate-0"));
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
    :class="[className, 'shrink-0 transition-transform', rotateClass]"
  >
    <path d="m6 9 6 6 6-6" />
  </svg>
</template>
