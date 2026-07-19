<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";

defineProps<{
  title: string;
  subtitle?: string;
  link: string;
  meta?: string;
}>();

const emit = defineEmits<{
  copy: [];
  delete: [];
}>();
</script>

<template>
  <Card hoverable>
    <div class="flex justify-between items-start">
      <div class="flex-1 min-w-0">
        <div class="text-surface-light font-bold text-sm truncate">{{ title }}</div>
        <div v-if="subtitle" class="text-xs text-surface-mid truncate mt-1">{{ subtitle }}</div>
        <div v-if="meta" class="text-xs text-surface-mid mt-1">{{ meta }}</div>
        <code class="text-xs text-accent-blue mt-2 block truncate">{{ link }}</code>
      </div>
      <div class="flex gap-2 ml-4">
        <BaseButton variant="ghost" size="sm" @click="emit('copy')">copy</BaseButton>
        <BaseButton variant="ghost" danger size="sm" @click="emit('delete')">delete</BaseButton>
      </div>
    </div>
  </Card>
</template>
