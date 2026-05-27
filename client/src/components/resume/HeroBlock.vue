<script setup lang="ts">
defineProps<{
  name: string;
  title: string;
  bio: string;
}>();
</script>

<template>
  <div class="py-20 text-center">
    <h1 class="text-5xl md:text-7xl font-bold mb-4">
      <span class="accent-gradient">{{ name }}</span>
    </h1>
    <p class="text-xl md:text-2xl text-surface-mid mb-6">{{ title }}</p>
    <p class="text-sm md:text-base text-surface-mid/80 max-w-2xl mx-auto leading-relaxed">
      {{ bio }}
    </p>
    <div class="mt-8 flex justify-center gap-4">
      <a
        href="#skills"
        class="px-6 py-2 rounded-lg bg-gradient-to-r from-accent-blue to-accent-violet text-white text-sm font-medium hover:opacity-90 transition-opacity"
      >
        View Skills
      </a>
      <a
        href="#projects"
        class="px-6 py-2 rounded-lg border border-surface-border text-surface-mid text-sm font-medium hover:border-accent-blue transition-colors"
      >
        Projects
      </a>
    </div>
  </div>
</template>
