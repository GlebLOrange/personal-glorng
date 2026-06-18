<script setup lang="ts">
import { computed } from "vue";

import BaseCard from "@/components/ui/BaseCard.vue";
import { groupServicesByCategory, publicToolsAsServices } from "@/platform/services";

const sections = computed(() => groupServicesByCategory(publicToolsAsServices()));
</script>

<template>
  <div class="max-w-5xl mx-auto px-6 py-10">
    <div class="mb-8">
      <h1 class="text-3xl font-bold accent-gradient mb-2">tools</h1>
      <p class="text-sm text-surface-mid">Public utilities available without signing in.</p>
    </div>

    <section v-for="section in sections" :key="section.category" class="mb-10">
      <h2 class="text-lg font-bold text-surface-light mb-4">{{ section.label }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <RouterLink v-for="tool in section.services" :key="tool.adminRoute" :to="tool.adminRoute">
          <BaseCard hoverable class="h-full">
            <div class="text-2xl mb-3">{{ tool.icon }}</div>
            <h3 class="text-surface-light font-bold mb-1">{{ tool.name }}</h3>
            <p class="text-xs text-surface-mid">{{ tool.description }}</p>
          </BaseCard>
        </RouterLink>
      </div>
    </section>

    <p class="text-xs text-surface-muted">
      <RouterLink to="/login" class="text-accent-blue hover:underline">Sign in</RouterLink>
      to unlock limited demo tools.
    </p>
  </div>
</template>
