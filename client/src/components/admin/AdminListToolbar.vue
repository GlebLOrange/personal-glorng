<template>
  <div
    v-if="$slots.start"
    class="mb-3 flex flex-wrap items-center justify-start gap-3 min-w-0"
  >
    <slot name="start" />
  </div>
</template>
