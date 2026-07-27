<script setup lang="ts">
import { actionFamilyClass } from "@/constants/httpStatusColors";

defineProps<{
  categoryOptions: string[];
}>();

const categoryFilter = defineModel<string | null>("categoryFilter", { required: true });

const chipClass = (active: boolean) => actionFamilyClass("1xx", active);
</script>

<template>
  <div
    class="flex flex-nowrap gap-2 overflow-x-auto pb-1"
    role="group"
    aria-label="filter by category"
  >
    <button
      type="button"
      class="shrink-0"
      :class="chipClass(categoryFilter === null)"
      :aria-pressed="categoryFilter === null"
      @click="categoryFilter = null"
    >
      all
    </button>
    <button
      v-for="category in categoryOptions"
      :key="category"
      type="button"
      class="shrink-0"
      :class="chipClass(categoryFilter === category)"
      :aria-pressed="categoryFilter === category"
      @click="categoryFilter = category"
    >
      {{ category }}
    </button>
  </div>
</template>
