<script setup lang="ts">
import type { SkillGroup } from "@/types";

defineProps<{
  skills: SkillGroup[];
}>();
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div v-for="group in skills" :key="group.category" class="min-w-0">
      <h3 class="card-title mb-2">
        {{ group.category }}
      </h3>
      <p v-if="group.summary" class="text-meta mb-3">
        {{ group.summary.replace(/\.$/, "") }}
      </p>
      <ul class="m-0 flex list-none flex-wrap gap-x-3 gap-y-1 p-0 text-sm text-surface-sage">
        <li v-for="item in group.items" :key="item">
          {{ item }}
        </li>
      </ul>
    </div>
  </div>
</template>
