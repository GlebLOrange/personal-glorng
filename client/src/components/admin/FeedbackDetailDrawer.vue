<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { formatDate } from "@/utils/format";

interface FeedbackItem {
  id: number;
  email: string;
  theme: string;
  message: string;
  status: string;
  created_at: string;
}

defineProps<{
  open: boolean;
  item: FeedbackItem | null;
}>();

const emit = defineEmits<{
  close: [];
  reply: [];
  archive: [];
}>();

const statusColors: Record<string, string> = {
  unread: "bg-accent-blue/20 text-accent-blue border-accent-blue/30",
  read: "bg-surface-border text-surface-mid border-surface-border",
  archived: "bg-surface-dark text-surface-muted border-surface-border",
};
</script>

<template>
  <BaseDrawer
    :open="open && item !== null"
    :title="item?.theme ?? 'Feedback'"
    max-width="md"
    @close="emit('close')"
  >
    <template v-if="item">
      <div class="mb-4 flex flex-wrap items-center gap-2">
        <StatusBadge :label="item.status" :class-name="statusColors[item.status] ?? statusColors.read" />
        <span class="text-xs text-surface-muted">{{ item.email }} · {{ formatDate(item.created_at) }}</span>
      </div>
      <p class="whitespace-pre-wrap break-words text-sm text-surface-sage">{{ item.message }}</p>
    </template>

    <template #footer>
      <div class="flex gap-3">
        <BaseButton variant="primary" @click="emit('reply')">Reply</BaseButton>
        <BaseButton
          v-if="item && item.status !== 'archived'"
          variant="ghost"
          @click="emit('archive')"
        >
          Archive
        </BaseButton>
        <BaseButton variant="ghost" @click="emit('close')">Close</BaseButton>
      </div>
    </template>
  </BaseDrawer>
</template>
