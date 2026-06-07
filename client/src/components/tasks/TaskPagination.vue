<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";

defineProps<{
  page: number;
  hasNextPage: boolean;
}>();

const emit = defineEmits<{ prev: []; next: [] }>();
</script>

<template>
  <div class="flex items-center justify-between pt-4">
    <BaseButton variant="ghost" size="sm" :disabled="page <= 1" @click="emit('prev')">
      Previous
    </BaseButton>
    <span class="text-xs text-surface-mid">Page {{ page }}</span>
    <BaseButton variant="ghost" size="sm" :disabled="!hasNextPage" @click="emit('next')">
      Next
    </BaseButton>
  </div>
</template>
