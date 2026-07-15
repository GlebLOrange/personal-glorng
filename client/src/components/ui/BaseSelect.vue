<script setup lang="ts">
import { computed, useId } from "vue";

import { SELECT_CLASS, SELECT_CLASS_COMPACT } from "@/constants/formClasses";

const model = defineModel<string | number | null>();

const props = defineProps<{
  id?: string;
  label?: string;
  compact?: boolean;
}>();

const fallbackId = useId();
const selectId = computed(() => props.id ?? `base-select-${fallbackId}`);
const selectClass = computed(() => (props.compact ? SELECT_CLASS_COMPACT : SELECT_CLASS));
</script>

<template>
  <div class="flex flex-col gap-1">
    <select :id="selectId" v-model="model" :class="selectClass">
      <slot />
    </select>
  </div>
</template>
