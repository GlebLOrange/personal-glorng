<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import { Card, CardBody } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import { passwordStrength } from "@/utils/passwordPolicy";

const newEmail = defineModel<string>("newEmail", { required: true });
const emailPassword = defineModel<string>("emailPassword", { required: true });
const currentPassword = defineModel<string>("currentPassword", { required: true });
const newPassword = defineModel<string>("newPassword", { required: true });
const newPasswordConfirm = defineModel<string>("newPasswordConfirm", { required: true });

defineProps<{
  permissions: string[];
  savingEmail: boolean;
  canSaveEmail: boolean;
  savingPassword: boolean;
  canSavePassword: boolean;
}>();

const emit = defineEmits<{
  saveEmail: [];
  savePassword: [];
  logout: [];
}>();

const passwordCheck = computed(() => passwordStrength(newPassword.value));
const passwordsMatch = computed(
  () => !!newPasswordConfirm.value && newPassword.value === newPasswordConfirm.value,
);
</script>

<template>
  <Card variant="compact">
    <CardBody>
      <div class="space-y-4">
        <form class="space-y-2" @submit.prevent="emit('saveEmail')">
          <BaseInput
            v-model="newEmail"
            type="email"
            name="email"
            autocomplete="email"
            placeholder="email address"
            aria-label="email address"
            required
          />
          <div class="flex min-w-0 items-center gap-2">
            <BaseInput
              v-model="emailPassword"
              class="min-w-0 flex-1"
              type="password"
              name="current-password-for-email"
              autocomplete="current-password"
              placeholder="current password"
              aria-label="current password for email change"
              required
            />
            <BaseButton
              type="submit"
              variant="save"
              size="sm"
              class="shrink-0"
              :loading="savingEmail"
              :disabled="!canSaveEmail"
            >
              {{ savingEmail ? "saving…" : "change email" }}
            </BaseButton>
          </div>
        </form>

        <form
          class="space-y-2 border-t border-surface-border pt-4"
          @submit.prevent="emit('savePassword')"
        >
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
          <div class="flex items-center justify-between gap-2">
            <RouterLink
              to="/forgot-password"
              class="text-xs text-accent-coral hover:underline focus:underline"
            >
              forgot password?
            </RouterLink>
            <BaseButton
              type="submit"
              variant="save"
              size="sm"
              :loading="savingPassword"
              :disabled="!canSavePassword"
            >
              {{ savingPassword ? "saving…" : "change password" }}
            </BaseButton>
          </div>
        </form>

        <div class="border-t border-surface-border pt-4">
          <p class="mb-2 text-xs text-surface-mid">permissions</p>
          <div v-if="permissions.length" class="flex flex-wrap gap-1.5">
            <span
              v-for="perm in permissions"
              :key="perm"
              class="break-words rounded-full border border-surface-border px-2 py-0.5 text-xs text-surface-muted"
            >
              {{ perm }}
            </span>
          </div>
          <p v-else class="text-xs text-surface-mid">No tool permissions — contact an admin.</p>
        </div>

        <div class="border-t border-surface-border pt-4">
          <BaseButton type="button" variant="secondary" size="sm" danger @click="emit('logout')">
            log out
          </BaseButton>
          <p class="mt-2 text-xs text-surface-mid">Signs out this device only.</p>
        </div>
      </div>
    </CardBody>
  </Card>
</template>
