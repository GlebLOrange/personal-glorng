<script setup lang="ts">
import { Card } from "@/components/ui/card";
import type { SkillGroup } from "@/types";

defineProps<{
  skills: SkillGroup[];
}>();
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <Card v-for="group in skills" :key="group.category">
      <h3 class="card-title text-accent-blue mb-2">
        {{ group.category }}
      </h3>
      <p v-if="group.summary" class="text-meta mb-3">
        {{ group.summary }}
      </p>
      <div class="flex flex-wrap gap-2">
        <span
          v-for="item in group.items"
          :key="item"
          class="rounded-lg border border-surface-border px-3 py-1.5 text-sm text-surface-light bg-surface-dark/50"
        >
          {{ item }}
        </span>
      </div>
    </Card>
  </div>
</template>
