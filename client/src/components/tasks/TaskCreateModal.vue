<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
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
      <BaseInput
        v-model="form.title"
        placeholder="title (what needs doing?)"
        aria-label="title (what needs doing?)"
      />
      <BaseInput
        v-model="form.scheduled_at"
        type="datetime-local"
        aria-label="scheduled at"
      />
      <BaseInput
        v-model="form.location"
        placeholder="location (optional)"
        aria-label="location (optional)"
      />
      <textarea
        v-model="form.description"
        rows="3"
        placeholder="notes (optional)"
        aria-label="notes (optional)"
        :class="[FIELD_INPUT_CLASS, 'h-auto resize-none']"
      />
    </form>

    <template #footer>
      <div class="flex gap-3">
        <BaseButton
          type="submit"
          form="task-create-drawer-form"
          variant="primary"
          :disabled="saving"
        >
          {{ saving ? "creating..." : "create" }}
        </BaseButton>
        <BaseButton variant="ghost" type="button" @click="emit('close')">cancel</BaseButton>
      </div>
    </template>
  </BaseDrawer>
</template>
