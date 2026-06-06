<script setup lang="ts">
import { computed } from "vue";

import { SELECT_CLASS, SELECT_CLASS_COMPACT } from "@/constants/formClasses";

const model = defineModel<string | number | null>();

const props = defineProps<{
  label?: string;
  compact?: boolean;
}>();

const selectClass = computed(() => (props.compact ? SELECT_CLASS_COMPACT : SELECT_CLASS));
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" class="text-sm text-surface-mid">{{ label }}</label>
    <select v-model="model" :class="selectClass">
      <slot />
    </select>
  </div>
</template>
