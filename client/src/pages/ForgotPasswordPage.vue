<script setup lang="ts">
import { ref } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";

const { toast } = useNotify();

const email = ref("");
const loading = ref(false);
const submitted = ref(false);

async function handleSubmit(): Promise<void> {
  loading.value = true;
  try {
    await api.post("/auth/forgot-password", { email: email.value });
    submitted.value = true;
    toast("If the email exists, a reset link was sent", "success");
  } catch (err) {
    toast(getApiErrorMessage(err, "Request failed"), "error");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-6">
    <div class="w-full max-w-sm">
      <h1 class="text-2xl font-bold text-surface-light mb-8 text-center">
        <span class="accent-gradient">reset password</span>
      </h1>

      <p v-if="submitted" class="text-surface-mid text-sm text-center">
        If an account exists for {{ email }}, you will receive a reset link shortly.
      </p>

      <form v-else class="space-y-4" @submit.prevent="handleSubmit">
        <BaseInput
          v-model="email"
          type="email"
          label="Email"
          placeholder="you@example.com"
          required
        />
        <BaseButton variant="primary" class="w-full" :disabled="loading">
          {{ loading ? "Sending..." : "Send reset link" }}
        </BaseButton>
      </form>

      <p class="text-center text-xs text-surface-mid mt-6">
        <RouterLink to="/login" class="text-accent-blue hover:underline"
          >BACK</RouterLink
        >
      </p>
    </div>
  </div>
</template>
