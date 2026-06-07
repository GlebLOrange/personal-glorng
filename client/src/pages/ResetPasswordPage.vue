<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import { passwordStrength } from "@/utils/passwordPolicy";

const route = useRoute();
const router = useRouter();
const { toast } = useNotify();

const token = ref("");
const password = ref("");
const passwordConfirm = ref("");
const loading = ref(false);

const strength = computed(() => passwordStrength(password.value));

onMounted(() => {
  const raw = route.query.token;
  token.value = typeof raw === "string" ? raw : "";
});

async function handleSubmit(): Promise<void> {
  if (!token.value) {
    toast("Missing reset token", "error");
    return;
  }

  loading.value = true;
  try {
    await api.post("/auth/reset-password", {
      token: token.value,
      new_password: password.value,
      password_confirm: passwordConfirm.value,
    });
    toast("Password reset successfully", "success");
    router.push("/login");
  } catch (err) {
    toast(getApiErrorMessage(err, "Reset failed"), "error");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-6">
    <div class="w-full max-w-sm">
      <h1 class="text-2xl font-bold text-surface-light mb-8 text-center">
        <span class="accent-gradient">new password</span>
      </h1>

      <form v-if="token" class="space-y-4" @submit.prevent="handleSubmit">
        <BaseInput
          v-model="password"
          type="password"
          label="New password"
          placeholder="••••••••••••"
          required
        />
        <p class="text-xs" :class="strength.valid ? 'text-green-400' : 'text-surface-mid'">
          {{ strength.message }}
        </p>
        <BaseInput
          v-model="passwordConfirm"
          type="password"
          label="Confirm password"
          placeholder="••••••••••••"
          required
        />
        <BaseButton variant="primary" class="w-full" :disabled="loading || !strength.valid">
          {{ loading ? "Saving..." : "Set new password" }}
        </BaseButton>
      </form>

      <p v-else class="text-red-400 text-sm text-center">Invalid or missing reset link.</p>

      <p class="text-center text-xs text-surface-mid mt-6">
        <RouterLink to="/login" class="text-accent-blue hover:underline"
          >&larr; Back to login</RouterLink
        >
      </p>
    </div>
  </div>
</template>
