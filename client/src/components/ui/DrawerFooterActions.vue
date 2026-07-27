<script setup lang="ts">
withDefaults(
  defineProps<{
    /**
     * Cluster actions as content-width (end-aligned) instead of
     * dismiss left / primary right across the full footer.
     */
    cluster?: boolean;
  }>(),
  { cluster: false },
);
</script>

<template>
  <div
    class="flex flex-wrap items-center gap-2"
    :class="cluster ? 'ml-auto w-fit' : 'w-full justify-between'"
  >
    <template v-if="cluster">
      <slot name="start" />
      <slot name="dismiss" />
      <slot name="primary" />
    </template>
    <template v-else>
      <div class="flex flex-wrap items-center gap-2">
        <slot name="start" />
        <slot name="dismiss" />
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <slot name="primary" />
      </div>
    </template>
  </div>
</template>
