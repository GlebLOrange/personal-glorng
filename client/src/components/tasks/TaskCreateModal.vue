<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseModal from "@/components/ui/BaseModal.vue";
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
  <BaseModal v-if="open" title="New task" @close="emit('close')">
    <form class="space-y-4" @submit.prevent="emit('submit')">
      <BaseInput v-model="form.title" label="Title" placeholder="What needs doing?" />
      <BaseInput v-model="form.scheduled_at" label="Scheduled at" type="datetime-local" />
      <BaseInput v-model="form.location" label="Location" placeholder="Optional" />
      <div>
        <label class="text-sm text-surface-mid block mb-1">Notes</label>
        <textarea
          v-model="form.description"
          rows="3"
          placeholder="Optional details"
          :class="[FIELD_INPUT_CLASS, 'h-auto resize-none']"
        />
      </div>
      <div class="flex gap-3 pt-2">
        <BaseButton variant="primary" :disabled="saving">
          {{ saving ? "Creating..." : "Create" }}
        </BaseButton>
        <BaseButton variant="ghost" type="button" @click="emit('close')">Cancel</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>
