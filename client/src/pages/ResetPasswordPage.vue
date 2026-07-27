<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from "vue";
import { useRoute, useRouter } from "vue-router";

import AuthPageShell from "@/components/auth/AuthPageShell.vue";
import PasswordFields from "@/components/auth/PasswordFields.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import { consumeQueryParams } from "@/utils/consumeQueryParams";
import { focusAfterPaint, focusEditableField } from "@/utils/focusField";
import { passwordStrength } from "@/utils/passwordPolicy";

const route = useRoute();
const router = useRouter();
const { toast } = useNotify();

const token = ref("");
const password = ref("");
const passwordConfirm = ref("");
const loading = ref(false);
const formError = ref("");
const formErrorEl = useTemplateRef<HTMLElement>("formErrorAlert");
const formEl = useTemplateRef<HTMLFormElement>("resetForm");

const strength = computed(() => passwordStrength(password.value));
const passwordsMatch = computed(
  () => !!passwordConfirm.value && password.value === passwordConfirm.value,
);
const canSubmit = computed(
  () => !!token.value && strength.value.valid && passwordsMatch.value && !loading.value,
);

onMounted(async () => {
  const { token: raw } = await consumeQueryParams(router, route.path, route.query, ["token"]);
  token.value = typeof raw === "string" ? raw : "";
});

async function handleSubmit(): Promise<void> {
  if (!token.value) {
    toast("Missing reset token", "error");
    return;
  }
  if (!canSubmit.value) {
    focusEditableField(formEl.value);
    return;
  }

  loading.value = true;
  formError.value = "";
  try {
    await api.post("/auth/reset-password", {
      token: token.value,
      new_password: password.value,
      password_confirm: passwordConfirm.value,
    });
    toast("Password reset successfully", "success");
    router.push("/login");
  } catch (err) {
    formError.value = getApiErrorMessage(err, "Reset failed");
    toast(formError.value, "error");
    await focusAfterPaint(() => formErrorEl.value);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <AuthPageShell title="new password" back-to="/login">
    <form v-if="token" ref="resetForm" class="space-y-4" @submit.prevent="handleSubmit">
      <PasswordFields
        v-model:password="password"
        v-model:password-confirm="passwordConfirm"
        password-label="new password"
        password-placeholder="new password"
        strength-id="reset-password-strength"
      />
      <p
        v-if="formError"
        ref="formErrorAlert"
        class="text-xs text-status-error"
        role="alert"
        tabindex="-1"
      >
        {{ formError }}
      </p>
      <BaseButton
        type="submit"
        variant="primary"
        class="w-full"
        :loading="loading"
        :disabled="!canSubmit"
      >
        {{ loading ? "saving…" : "set new password" }}
      </BaseButton>
    </form>

    <div v-else class="space-y-3 text-center" role="alert">
      <p class="text-status-error text-sm">Invalid or missing reset link.</p>
      <RouterLink to="/forgot-password" class="nav-link text-sm">
        request a new reset link
      </RouterLink>
    </div>
  </AuthPageShell>
</template>
