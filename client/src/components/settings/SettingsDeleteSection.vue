<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";

const deletePassword = defineModel<string>("deletePassword", { required: true });
const deleteConfirm = defineModel<boolean>("deleteConfirm", { required: true });

defineProps<{
  deleting: boolean;
  canDelete: boolean;
}>();

const emit = defineEmits<{
  delete: [];
}>();
</script>

<template>
  <Card tint="danger">
    <CardBody>
      <CardHeader>
        <CardTitle>delete account</CardTitle>
      </CardHeader>
      <form class="space-y-4" @submit.prevent="emit('delete')">
        <BaseInput
          v-model="deletePassword"
          type="password"
          name="delete-current-password"
          autocomplete="current-password"
          placeholder="current password"
          aria-label="current password"
          required
        />
        <label class="flex min-h-11 cursor-pointer items-start gap-3 text-xs text-surface-mid">
          <input v-model="deleteConfirm" type="checkbox" class="mt-1 accent-status-error" />
          <span>I understand this permanently deletes my account.</span>
        </label>
        <BaseButton
          type="submit"
          variant="secondary"
          danger
          :loading="deleting"
          :disabled="!canDelete"
        >
          {{ deleting ? "deleting..." : "delete account" }}
        </BaseButton>
      </form>
    </CardBody>
  </Card>
</template>
