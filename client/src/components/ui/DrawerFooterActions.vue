<script setup lang="ts">
/** Shared drawer footer: dismiss left, primary right; optional start (e.g. delete). */
</script>

<template>
  <div class="flex w-full flex-wrap items-center justify-between gap-3">
    <div class="flex flex-wrap items-center gap-2">
      <slot name="start" />
      <slot name="dismiss" />
    </div>
    <div class="flex flex-wrap items-center gap-2">
      <slot name="primary" />
    </div>
  </div>
</template>
