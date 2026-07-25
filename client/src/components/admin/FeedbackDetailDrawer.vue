<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { feedbackStatusClass } from "@/constants/filterColors";
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
}>();
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
        <StatusBadge
          :label="item.status"
          size="md"
          :class-name="feedbackStatusClass(item.status)"
        />
        <span class="text-xs text-surface-muted"
          >{{ item.email }} · {{ formatDate(item.created_at) }}</span
        >
      </div>
      <p class="whitespace-pre-wrap break-words text-sm text-surface-sage">{{ item.message }}</p>
    </template>

    <template #footer>
      <DrawerFooterActions>
        <template #dismiss>
          <BaseButton
            variant="ghost"
            danger
            size="sm"
            class="hover:enabled:border-transparent focus-visible:border-transparent"
            @click="emit('close')"
          >
            close
          </BaseButton>
        </template>
        <template #primary>
          <ToolbarPillButton family="2xx" @click="emit('reply')">reply</ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseDrawer>
</template>
