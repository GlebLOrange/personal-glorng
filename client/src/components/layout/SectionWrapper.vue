<script setup lang="ts">
defineProps<{
  id?: string;
  title?: string;
  dark?: boolean;
  alternate?: boolean;
  centered?: boolean;
}>();
</script>

<template>
  <section
    :id="id"
    :class="[
      'py-20 md:py-24 px-6 scroll-mt-40 md:scroll-mt-44',
      alternate && 'bg-surface-card/30',
      dark ? 'text-surface-light' : 'text-surface-dark',
    ]"
  >
    <div class="page-tile-scope mx-auto w-full max-w-5xl">
      <div :class="centered ? 'w-full' : 'page-body-narrow w-full'">
        <h2 v-if="title" class="section-title mb-8">
          <span aria-hidden="true" class="text-accent-blue">€ </span>
          {{ title }}
        </h2>
        <slot />
      </div>
    </div>
  </section>
</template>
