<script setup lang="ts">
defineProps<{
  id?: string;
  title?: string;
  dark?: boolean;
}>();
</script>

<template>
  <section :id="id" :class="['py-16 px-6', dark ? 'text-surface-light' : 'text-surface-dark']">
    <div class="max-w-5xl mx-auto">
      <h2
        v-if="title"
        class="text-2xl font-bold mb-6"
        :class="dark ? 'text-surface-light' : 'text-surface-dark'"
      >
        <span aria-hidden="true" class="text-accent-blue">€ </span>
        {{ title }}
      </h2>
      <slot />
    </div>
  </section>
</template>
