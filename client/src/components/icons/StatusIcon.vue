<script setup lang="ts">
withDefaults(
  defineProps<{
    status: "success" | "error" | "warning";
    className?: string;
  }>(),
  { className: "size-8" },
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
    :class="[
      className,
      'shrink-0',
      status === 'success' ? 'text-status-success' : undefined,
      status === 'error' ? 'text-status-error' : undefined,
      status === 'warning' ? 'text-status-warning' : undefined,
    ]"
  >
    <template v-if="status === 'success'">
      <circle cx="12" cy="12" r="9" />
      <path d="m8 12 2.5 2.5L16 9" />
    </template>
    <template v-else-if="status === 'error'">
      <circle cx="12" cy="12" r="9" />
      <path d="m9 9 6 6M15 9l-6 6" />
    </template>
    <template v-else>
      <path d="M12 3 2.5 20h19L12 3z" />
      <path d="M12 10v5M12 17.5v.5" />
    </template>
  </svg>
</template>
