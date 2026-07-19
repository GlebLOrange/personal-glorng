<script setup lang="ts">
import { Card } from "@/components/ui/card";
import type { Education } from "@/types";

defineProps<{
  education: Education[];
}>();
</script>

<template>
  <div class="space-y-4">
    <Card v-for="(entry, i) in education" :key="i" variant="ghost">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between mb-2">
        <div class="min-w-0">
          <h3 class="card-title">{{ entry.degree }}</h3>
          <p class="text-base text-accent-blue">{{ entry.institution }}</p>
        </div>
        <span class="text-meta shrink-0">{{ entry.period }}</span>
      </div>
      <p v-if="entry.description" class="text-body">{{ entry.description }}</p>
    </Card>
  </div>
</template>
