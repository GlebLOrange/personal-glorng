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
        class="section-title"
        :class="dark ? 'text-surface-light' : 'text-surface-dark'"
      >
        {{ title }}
      </h2>
      <slot />
    </div>
  </section>
</template>
