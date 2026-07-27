<script setup lang="ts">
import { ref, useTemplateRef } from "vue";

import AuthPageShell from "@/components/auth/AuthPageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import { focusAfterPaint } from "@/utils/focusField";

const { toast } = useNotify();

const email = ref("");
const loading = ref(false);
const submitted = ref(false);
const formError = ref("");
const formErrorEl = useTemplateRef<HTMLElement>("formErrorAlert");

async function handleSubmit(): Promise<void> {
  loading.value = true;
  formError.value = "";
  try {
    await api.post("/auth/forgot-password", { email: email.value });
    submitted.value = true;
    toast("If the email exists, a reset link was sent", "success");
  } catch (err) {
    formError.value = getApiErrorMessage(err, "Request failed");
    toast(formError.value, "error");
    await focusAfterPaint(() => formErrorEl.value);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <AuthPageShell title="forgot password?" back-to="/login">
    <div v-if="submitted" class="space-y-4 text-center" role="status">
      <p class="text-surface-mid text-sm">
        If an account exists for {{ email }}, you will receive a reset link shortly.
      </p>
      <RouterLink to="/login" class="nav-link text-sm"> return to login </RouterLink>
    </div>

    <form v-else class="space-y-4" @submit.prevent="handleSubmit">
      <BaseInput
        v-model="email"
        type="email"
        name="email"
        autocomplete="email"
        label="email"
        required
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
      <BaseButton type="submit" variant="primary" class="w-full" :loading="loading">
        {{ loading ? "sending…" : "send reset link" }}
      </BaseButton>
    </form>
  </AuthPageShell>
</template>
