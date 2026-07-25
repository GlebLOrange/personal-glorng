<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { FIELD_INPUT_CLASS } from "@/constants/formClasses";
import type { TaskCreateForm } from "@/composables/useTasks";

defineProps<{
  open: boolean;
  saving: boolean;
}>();

const form = defineModel<TaskCreateForm>("form", { required: true });

const emit = defineEmits<{ submit: []; close: [] }>();
</script>

<template>
  <BaseDrawer :open="open" title="new task" max-width="md" @close="emit('close')">
    <form id="task-create-drawer-form" class="space-y-4" @submit.prevent="emit('submit')">
      <BaseInput v-model="form.title" placeholder="title (what needs doing?)" />
      <BaseInput v-model="form.scheduled_at" type="datetime-local" aria-label="scheduled at" />
      <BaseInput v-model="form.location" placeholder="location (optional)" />
      <textarea
        v-model="form.description"
        rows="3"
        placeholder="notes (optional)"
        :class="[FIELD_INPUT_CLASS, 'h-auto resize-none']"
      />
    </form>

    <template #footer>
      <DrawerFooterActions>
        <template #dismiss>
          <BaseButton variant="secondary" type="button" @click="emit('close')"> cancel </BaseButton>
        </template>
        <template #primary>
          <ToolbarPillButton
            type="submit"
            form="task-create-drawer-form"
            family="1xx"
            :disabled="saving"
          >
            {{ saving ? "creating..." : "create" }}
          </ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseDrawer>
</template>
