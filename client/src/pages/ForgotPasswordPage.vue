<script setup lang="ts">
import { ref } from "vue";

import BackLink from "@/components/ui/BackLink.vue";
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
        <span class="accent-gradient">forgot password</span>
      </h1>

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
          placeholder="you@example.com"
          required
        />
        <button type="submit" class="cta-primary w-full" :disabled="loading">
          {{ loading ? "sending..." : "send reset link" }}
        </button>
      </form>

      <p class="flex justify-center mt-6">
        <BackLink to="/login" />
      </p>
    </div>
  </div>
</template>
