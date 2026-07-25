<template>
  <div
    v-if="$slots.actions || $slots.default || $slots.start"
    class="mb-3 flex min-w-0 flex-wrap items-center gap-2"
  >
    <div
      v-if="$slots.actions"
      class="flex min-w-0 flex-wrap items-center gap-1"
      role="toolbar"
      aria-label="List actions"
    >
      <slot name="actions" />
    </div>
    <div v-if="$slots.default || $slots.start" class="flex min-w-0 flex-1 flex-wrap items-center gap-2">
      <slot />
      <slot name="start" />
    </div>
  </div>
</template>
