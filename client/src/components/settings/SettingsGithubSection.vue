<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import { Card, CardBody } from "@/components/ui/card";
import type { GitHubStatus } from "@/types";

defineProps<{
  status: GitHubStatus;
  loading: boolean;
  error: string | null;
  unlinking: boolean;
}>();

const emit = defineEmits<{
  connect: [];
  unlink: [];
  retry: [];
}>();
</script>

<template>
  <Card variant="compact">
    <CardBody>
      <div class="flex flex-wrap items-center gap-2">
        <p v-if="error" class="w-full text-sm text-status-warning">{{ error }}</p>
        <BaseButton
          v-if="!status.linked"
          variant="primary"
          size="sm"
          :disabled="loading"
          @click="emit('connect')"
        >
          connect github
        </BaseButton>
        <template v-else>
          <p class="text-sm text-surface-mid">
            Connected as
            <span class="font-medium text-surface-light"
              >@{{ status.github_username ?? "github" }}</span
            >
          </p>
          <BaseButton
            variant="secondary"
            size="sm"
            :disabled="unlinking"
            @click="emit('unlink')"
          >
            {{ unlinking ? "unlinking..." : "unlink" }}
          </BaseButton>
        </template>
        <BaseButton
          v-if="error"
          variant="ghost"
          size="sm"
          class="gap-1.5"
          :disabled="loading"
          @click="emit('retry')"
        >
          <RefreshIcon class-name="size-3.5" />
          retry
        </BaseButton>
      </div>
    </CardBody>
  </Card>
</template>
