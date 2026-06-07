<script setup lang="ts">
defineProps<{
  name: string;
  title: string;
  bio: string;
}>();
</script>

<template>
  <div class="py-20 text-center">
    <h1 class="text-5xl md:text-7xl font-bold mb-4 text-balance">
      <span class="accent-gradient">{{ name }}</span>
    </h1>
    <p class="text-xl md:text-2xl text-surface-mid mb-6">{{ title }}</p>
    <p class="text-base md:text-lg text-surface-sage max-w-2xl mx-auto leading-relaxed text-pretty">
      {{ bio }}
    </p>
    <div class="mt-8 flex justify-center gap-4">
      <a href="#skills" class="cta-primary"> View Skills </a>
      <a href="#projects" class="cta-secondary"> Projects </a>
    </div>
  </div>
</template>
