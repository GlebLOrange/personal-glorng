<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
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
const formError = ref("");

const strength = computed(() => passwordStrength(password.value));
const passwordsMatch = computed(
  () => !!passwordConfirm.value && password.value === passwordConfirm.value,
);
const canSubmit = computed(
  () => !!token.value && strength.value.valid && passwordsMatch.value && !loading.value,
);

onMounted(() => {
  const raw = route.query.token;
  token.value = typeof raw === "string" ? raw : "";
});

async function handleSubmit(): Promise<void> {
  if (!token.value) {
    toast("Missing reset token", "error");
    return;
  }
  if (!passwordsMatch.value) {
    formError.value = "Passwords do not match";
    return;
  }
  if (!canSubmit.value) return;

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
          name="password"
          autocomplete="new-password"
          label="new password"
          placeholder="new password"
          aria-describedby="reset-password-strength"
          :error="formError || undefined"
          required
        />
        <p
          id="reset-password-strength"
          class="text-xs"
          :class="strength.valid ? 'text-status-success' : 'text-surface-mid'"
        >
          {{ strength.message }}
        </p>
        <BaseInput
          v-model="passwordConfirm"
          type="password"
          name="password-confirm"
          autocomplete="new-password"
          label="confirm password"
          placeholder="confirm password"
          :error="passwordConfirm && !passwordsMatch ? 'Passwords do not match' : undefined"
          required
        />
        <BaseButton type="submit" variant="primary" class="w-full" :loading="loading" :disabled="!canSubmit">
          {{ loading ? "saving..." : "set new password" }}
        </BaseButton>
      </form>

      <div v-else class="space-y-3 text-center" role="alert">
        <p class="text-status-error text-sm">Invalid or missing reset link.</p>
        <RouterLink to="/forgot-password" class="nav-link text-sm">
          request a new reset link
        </RouterLink>
      </div>

      <p class="flex justify-center mt-6">
        <BackLink to="/login" />
      </p>
    </div>
  </div>
</template>
