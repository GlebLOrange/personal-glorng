<script setup lang="ts">
defineProps<{
  name: string;
  title: string;
  bio: string;
}>();
</script>

<template>
  <div class="py-12 md:py-20 text-center">
    <h1 class="text-4xl sm:text-5xl md:text-6xl font-bold mb-4 text-balance">
      <span class="accent-gradient">{{ name }}</span>
    </h1>
    <p class="text-2xl md:text-3xl text-surface-sage mb-6">{{ title }}</p>
    <p class="text-lg md:text-xl max-w-2xl mx-auto text-surface-sage leading-relaxed text-pretty">
      {{ bio }}
    </p>
    <div class="mt-8 flex flex-col sm:flex-row justify-center gap-4">
      <a href="#skills" class="cta-primary"> View Skills </a>
      <a href="#projects" class="cta-secondary"> Projects </a>
    </div>
  </div>
</template>
