<template>
  <div
    v-if="$slots.actions || $slots.default || $slots.start"
    class="mb-3 flex w-full min-w-0 flex-wrap items-center gap-2"
  >
    <div
      v-if="$slots.default || $slots.start"
      class="flex min-w-0 flex-1 flex-wrap items-center gap-2"
    >
      <slot name="start" />
      <slot />
    </div>
    <div
      v-if="$slots.actions"
      class="ml-auto flex min-w-0 flex-wrap items-center justify-end gap-1"
      role="toolbar"
      aria-label="list actions"
    >
      <slot name="actions" />
    </div>
  </div>
</template>
