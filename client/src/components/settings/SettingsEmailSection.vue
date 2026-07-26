<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";

const newEmail = defineModel<string>("newEmail", { required: true });
const emailPassword = defineModel<string>("emailPassword", { required: true });

defineProps<{
  saving: boolean;
  canSave: boolean;
}>();

const emit = defineEmits<{
  save: [];
}>();
</script>

<template>
  <Card>
    <CardBody>
      <CardHeader>
        <CardTitle>email</CardTitle>
      </CardHeader>
      <form class="space-y-4" @submit.prevent="emit('save')">
        <BaseInput
          v-model="newEmail"
          type="email"
          name="email"
          autocomplete="email"
          placeholder="email address"
          aria-label="email address"
          required
        />
        <BaseInput
          v-model="emailPassword"
          type="password"
          name="current-password-for-email"
          autocomplete="current-password"
          placeholder="current password"
          aria-label="current password"
          required
        />
        <BaseButton type="submit" variant="success" :loading="saving" :disabled="!canSave">
          {{ saving ? "saving..." : "change email" }}
        </BaseButton>
      </form>
    </CardBody>
  </Card>
</template>
