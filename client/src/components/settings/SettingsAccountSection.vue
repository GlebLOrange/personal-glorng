<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import { passwordStrength } from "@/utils/passwordPolicy";

const newEmail = defineModel<string>("newEmail", { required: true });
const emailPassword = defineModel<string>("emailPassword", { required: true });
const currentPassword = defineModel<string>("currentPassword", { required: true });
const newPassword = defineModel<string>("newPassword", { required: true });
const newPasswordConfirm = defineModel<string>("newPasswordConfirm", { required: true });

defineProps<{
  savingEmail: boolean;
  canSaveEmail: boolean;
  savingPassword: boolean;
  canSavePassword: boolean;
}>();

const emit = defineEmits<{
  saveEmail: [];
  savePassword: [];
}>();

const passwordCheck = computed(() => passwordStrength(newPassword.value));
const passwordsMatch = computed(
  () => !!newPasswordConfirm.value && newPassword.value === newPasswordConfirm.value,
);
</script>

<template>
  <Card variant="compact">
    <CardBody>
      <CardHeader class="!mb-2">
        <CardTitle>account</CardTitle>
      </CardHeader>
      <div class="space-y-4">
        <form class="space-y-2" @submit.prevent="emit('saveEmail')">
          <p class="text-xs text-surface-mid">email</p>
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
            aria-label="current password for email change"
            required
          />
          <BaseButton
            type="submit"
            variant="success"
            size="sm"
            :loading="savingEmail"
            :disabled="!canSaveEmail"
          >
            {{ savingEmail ? "saving…" : "change email" }}
          </BaseButton>
        </form>

        <form class="space-y-2" @submit.prevent="emit('savePassword')">
          <div class="flex items-center justify-between gap-2">
            <p class="text-xs text-surface-mid">password</p>
            <RouterLink
              to="/forgot-password"
              class="text-xs text-accent-blue hover:underline focus:underline"
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
          <BaseButton
            type="submit"
            variant="success"
            size="sm"
            :loading="savingPassword"
            :disabled="!canSavePassword"
          >
            {{ savingPassword ? "saving…" : "change password" }}
          </BaseButton>
        </form>
      </div>
    </CardBody>
  </Card>
</template>
