<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import SyncIcon from "@/components/icons/SyncIcon.vue";
import { Card } from "@/components/ui/card";

withDefaults(
  defineProps<{
    message: string;
    retryLabel?: string;
    showRetry?: boolean;
    /** Icon for the retry control — sync for calendar/live sync, refresh otherwise. */
    retryIcon?: "refresh" | "sync";
  }>(),
  {
    retryLabel: "retry",
    showRetry: false,
    retryIcon: "refresh",
  },
);

const emit = defineEmits<{ retry: [] }>();
</script>

<template>
  <Card as="section" role="alert" class="!p-8 text-center">
    <p class="mb-4 text-sm text-status-error">{{ message }}</p>
    <BaseButton v-if="showRetry" variant="ghost" size="sm" class="gap-1.5" @click="emit('retry')">
      <SyncIcon v-if="retryIcon === 'sync'" class-name="size-3.5" />
      <RefreshIcon v-else class-name="size-3.5" />
      {{ retryLabel }}
    </BaseButton>
  </Card>
</template>
