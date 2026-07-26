<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
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
  <Card>
    <CardBody>
      <CardHeader>
        <CardTitle>github</CardTitle>
      </CardHeader>
      <div class="space-y-4">
        <p v-if="error" class="text-sm text-status-warning">{{ error }}</p>
        <div class="flex flex-wrap items-center gap-3">
          <BaseButton
            v-if="!status.linked"
            variant="primary"
            :disabled="loading"
            @click="emit('connect')"
          >
            connect github
          </BaseButton>
          <template v-else>
            <p class="text-sm text-surface-mid">
              Connected as
              <span class="text-surface-light font-medium"
                >@{{ status.github_username ?? "github" }}</span
              >
            </p>
            <BaseButton variant="secondary" :disabled="unlinking" @click="emit('unlink')">
              {{ unlinking ? "unlinking..." : "unlink github" }}
            </BaseButton>
          </template>
          <BaseButton
            v-if="error"
            variant="ghost"
            class="gap-1.5"
            :disabled="loading"
            @click="emit('retry')"
          >
            <RefreshIcon class-name="size-3.5" />
            retry
          </BaseButton>
        </div>
      </div>
    </CardBody>
  </Card>
</template>
