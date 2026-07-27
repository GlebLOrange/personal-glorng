<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
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

function displayMessage(message: string): string {
  return message.replace(/\.+\s*$/, "").trimEnd();
}
</script>

<template>
  <BaseDrawer
    :open="open && item !== null"
    :title="(item?.theme ?? 'feedback').toLowerCase()"
    :header-class="item ? feedbackStatusClass(item.status) : undefined"
    max-width="md"
    @close="emit('close')"
  >
    <template v-if="item">
      <p class="mb-4 text-xs text-surface-muted">
        {{ item.email }} · {{ formatDate(item.created_at) }}
      </p>
      <p class="whitespace-pre-wrap break-words text-sm lowercase text-surface-sage">
        {{ displayMessage(item.message) }}
      </p>
    </template>

    <template #footer>
      <DrawerFooterActions>
        <template #dismiss>
          <BaseButton danger size="sm" @click="emit('close')"> close </BaseButton>
        </template>
        <template #primary>
          <ToolbarPillButton family="2xx" @click="emit('reply')">reply</ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseDrawer>
</template>
