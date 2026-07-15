<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";

defineProps<{
  hasActiveFilters?: boolean;
}>();

const emit = defineEmits<{
  apply: [];
  clear: [];
}>();
</script>

<template>
  <Card class="mb-6">
    <div class="flex flex-wrap items-end gap-3">
      <slot />
      <BaseButton size="sm" @click="emit('apply')">Filter</BaseButton>
      <BaseButton
        v-if="hasActiveFilters"
        variant="ghost"
        size="sm"
        @click="emit('clear')"
      >
        Clear
      </BaseButton>
    </div>
  </Card>
</template>
