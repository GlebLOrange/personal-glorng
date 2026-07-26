<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import { passwordStrength } from "@/utils/passwordPolicy";

const currentPassword = defineModel<string>("currentPassword", { required: true });
const newPassword = defineModel<string>("newPassword", { required: true });
const newPasswordConfirm = defineModel<string>("newPasswordConfirm", { required: true });

defineProps<{
  saving: boolean;
  canSave: boolean;
}>();

const emit = defineEmits<{
  save: [];
}>();

const passwordCheck = computed(() => passwordStrength(newPassword.value));
const passwordsMatch = computed(
  () => !!newPasswordConfirm.value && newPassword.value === newPasswordConfirm.value,
);
</script>

<template>
  <Card>
    <CardBody>
      <CardHeader>
        <CardTitle>password</CardTitle>
      </CardHeader>
      <form class="space-y-4" @submit.prevent="emit('save')">
        <div class="flex justify-end">
          <RouterLink
            to="/forgot-password"
            class="text-sm text-accent-blue hover:underline focus:underline"
          >
            forgot password?
          </RouterLink>
        </div>
        <BaseInput
          v-model="currentPassword"
          type="password"
          name="current-password"
          autocomplete="current-password"
          placeholder="current password"
          aria-label="current password"
          required
        />
        <BaseInput
          v-model="newPassword"
          type="password"
          name="new-password"
          autocomplete="new-password"
          placeholder="new password"
          aria-label="new password"
          :error="newPassword && !passwordCheck.valid ? passwordCheck.message : undefined"
          required
        />
        <BaseInput
          v-model="newPasswordConfirm"
          type="password"
          name="confirm-new-password"
          autocomplete="new-password"
          placeholder="confirm new password"
          aria-label="confirm new password"
          :error="newPasswordConfirm && !passwordsMatch ? 'Passwords do not match' : undefined"
          required
        />
        <BaseButton type="submit" variant="success" :loading="saving" :disabled="!canSave">
          {{ saving ? "saving..." : "change password" }}
        </BaseButton>
      </form>
    </CardBody>
  </Card>
</template>
