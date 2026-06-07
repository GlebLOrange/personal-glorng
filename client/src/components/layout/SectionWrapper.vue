<script setup lang="ts">
defineProps<{
  id?: string;
  title?: string;
  dark?: boolean;
  alternate?: boolean;
}>();
</script>

<template>
  <section
    :id="id"
    :class="[
      'py-20 md:py-24 px-6 scroll-mt-24',
      alternate && 'bg-surface-card/30',
      dark ? 'text-surface-light' : 'text-surface-dark',
    ]"
  >
    <div class="max-w-5xl mx-auto">
      <h2 v-if="title" class="section-title mb-8">
        <span aria-hidden="true" class="text-accent-blue">€ </span>
        {{ title }}
      </h2>
      <slot />
    </div>
  </section>
</template>
