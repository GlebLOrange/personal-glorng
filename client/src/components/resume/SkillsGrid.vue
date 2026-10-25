<script setup lang="ts">
import { Card } from "@/components/ui/card";
import {
  PORTFOLIO_CV_CHIP_CLASS,
  PORTFOLIO_CV_TILE_CLASS,
} from "@/constants/portfolioSections";
import type { SkillGroup } from "@/types";

defineProps<{
  skills: SkillGroup[];
}>();
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <Card
      v-for="group in skills"
      :key="group.category"
      variant="compact"
      :class="['min-w-0 h-full', PORTFOLIO_CV_TILE_CLASS]"
    >
      <h3 class="card-title mb-1">
        {{ group.category }}
      </h3>
      <p v-if="group.summary" class="text-body mb-4">
        {{ group.summary.replace(/\.$/, "") }}
      </p>
      <ul class="m-0 flex list-none flex-wrap gap-2 p-0">
        <li
          v-for="item in group.items"
          :key="item"
          :class="[PORTFOLIO_CV_CHIP_CLASS, 'text-xs']"
        >
          {{ item }}
        </li>
      </ul>
    </Card>
  </div>
</template>
