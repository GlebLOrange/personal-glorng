<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
import LocationIcon from "@/components/icons/LocationIcon.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import TaskReminderScheduleInfo from "@/components/tasks/TaskReminderScheduleInfo.vue";
import type { TaskCreateErrors, TaskCreateForm } from "@/composables/useTasks";

withDefaults(
  defineProps<{
    open: boolean;
    saving: boolean;
    errors?: TaskCreateErrors;
  }>(),
  {
    errors: () => ({}),
  },
);

const form = defineModel<TaskCreateForm>("form", { required: true });

const emit = defineEmits<{ submit: []; close: [] }>();
</script>

<template>
  <BaseDrawer :open="open" title="new task" max-width="md" @close="emit('close')">
    <form id="task-create-drawer-form" class="space-y-4" @submit.prevent="emit('submit')">
      <BaseInput v-model="form.title" label="title" :error="errors.title" />
      <BaseInput
        v-model="form.scheduled_at"
        type="datetime-local"
        label="scheduled at"
        :error="errors.scheduled_at"
      />
      <TaskReminderScheduleInfo />
      <BaseInput v-model="form.location" label="location" placeholder="(optional)">
        <template #prefix>
          <LocationIcon class-name="size-4 shrink-0" />
        </template>
      </BaseInput>
      <BaseTextarea
        v-model="form.description"
        label="notes"
        :rows="3"
        placeholder="(optional)"
      />
    </form>

    <template #footer>
      <DrawerFooterActions>
        <template #dismiss>
          <BaseButton variant="cancel" type="button" @click="emit('close')"> cancel </BaseButton>
        </template>
        <template #primary>
          <ToolbarPillButton
            type="submit"
            form="task-create-drawer-form"
            action="create"
            :disabled="saving"
          >
            {{ saving ? "creating…" : "create" }}
          </ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseDrawer>
</template>
