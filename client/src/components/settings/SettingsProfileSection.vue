<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";

const displayName = defineModel<string>("displayName", { required: true });

defineProps<{
  saving: boolean;
  canSave: boolean;
}>();

const emit = defineEmits<{
  save: [];
}>();
</script>

<template>
  <Card variant="compact">
    <CardBody>
      <CardHeader class="!mb-2">
        <CardTitle>profile</CardTitle>
      </CardHeader>
      <form class="space-y-2" @submit.prevent="emit('save')">
        <BaseInput
          v-model="displayName"
          name="display-name"
          autocomplete="name"
          placeholder="display name"
          aria-label="display name"
        />
        <BaseButton
          type="submit"
          variant="success"
          size="sm"
          :loading="saving"
          :disabled="!canSave"
        >
          {{ saving ? "saving…" : "save" }}
        </BaseButton>
      </form>
    </CardBody>
  </Card>
</template>
