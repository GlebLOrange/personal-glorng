<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";

withDefaults(
  defineProps<{
    message: string;
    retryLabel?: string;
    showRetry?: boolean;
  }>(),
  {
    retryLabel: "Retry",
    showRetry: false,
  },
);

const emit = defineEmits<{ retry: [] }>();
</script>

<template>
  <Card as="section" role="alert" class="!p-8 text-center">
    <p class="text-sm text-surface-mid mb-4">{{ message }}</p>
    <BaseButton v-if="showRetry" variant="ghost" @click="emit('retry')">
      {{ retryLabel }}
    </BaseButton>
  </Card>
</template>
