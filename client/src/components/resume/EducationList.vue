<script setup lang="ts">
import { Card } from "@/components/ui/card";
import type { Education } from "@/types";

defineProps<{
  education: Education[];
}>();
</script>

<template>
  <div class="space-y-4">
    <Card v-for="(entry, i) in education" :key="i" hoverable>
      <div class="flex justify-between items-start mb-2 gap-4">
        <div>
          <h3 class="card-title">{{ entry.degree }}</h3>
          <p class="text-base text-accent-blue">{{ entry.institution }}</p>
        </div>
        <span class="text-meta shrink-0">{{ entry.period }}</span>
      </div>
      <p v-if="entry.description" class="text-body">{{ entry.description }}</p>
    </Card>
  </div>
</template>
