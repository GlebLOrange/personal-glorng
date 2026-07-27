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

function toggleConfirm(): void {
  deleteConfirm.value = !deleteConfirm.value;
}
</script>

<template>
  <Card variant="compact" tint="danger">
    <CardBody>
      <CardHeader class="!mb-2">
        <CardTitle>delete account</CardTitle>
      </CardHeader>
      <form class="space-y-2" @submit.prevent="emit('delete')">
        <BaseInput
          v-model="deletePassword"
          type="password"
          name="delete-current-password"
          autocomplete="current-password"
          placeholder="current password"
          aria-label="current password"
          required
        />
        <button
          type="button"
          class="inline-flex min-h-11 cursor-pointer items-center rounded px-2.5 py-1 text-left text-sm lowercase transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
          :class="
            deleteConfirm
              ? 'bg-accent-blue/10 text-accent-blue'
              : 'bg-surface-dark/60 text-surface-mid hover:text-surface-light'
          "
          :aria-pressed="deleteConfirm"
          @click="toggleConfirm"
        >
          I understand this permanently deletes my account.
        </button>
        <BaseButton
          type="submit"
          variant="secondary"
          danger
          size="sm"
          :loading="deleting"
          :disabled="!canDelete"
        >
          {{ deleting ? "deleting..." : "delete account" }}
        </BaseButton>
      </form>
    </CardBody>
  </Card>
</template>
