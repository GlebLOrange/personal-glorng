<script setup lang="ts">
import { computed, ref, useTemplateRef } from "vue";
import { useRoute, useRouter } from "vue-router";

import AuthPageShell from "@/components/auth/AuthPageShell.vue";
import GoogleMarkIcon from "@/components/icons/GoogleMarkIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { isFirebaseEnabled } from "@/constants/firebase";
import { useNotify } from "@/composables/useNotify";
import { useAuthStore } from "@/stores/auth";
import { getApiErrorMessage } from "@/types/api";
import { focusAfterPaint } from "@/utils/focusField";
import { safeRedirectPath } from "@/utils/safeUrl";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const { toast } = useNotify();

const email = ref("");
const password = ref("");
const loading = ref(false);
const googleLoading = ref(false);
const formError = ref("");
const formErrorEl = useTemplateRef<HTMLElement>("formErrorAlert");

const canSubmit = computed(() => !!email.value.trim() && !!password.value && !loading.value);

async function handleLogin(): Promise<void> {
  if (!canSubmit.value) return;
  loading.value = true;
  formError.value = "";
  try {
    await auth.login(email.value, password.value);
    toast("Logged in successfully", "success");
    router.push(safeRedirectPath(route.query.redirect));
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    formError.value = getApiErrorMessage(err, "Invalid email or password");
    toast(formError.value, "error");
    await focusAfterPaint(() => formErrorEl.value);
  } finally {
    loading.value = false;
  }
}

async function handleGoogleLogin(): Promise<void> {
  googleLoading.value = true;
  formError.value = "";
  try {
    await auth.loginWithGoogle();
    toast("Logged in successfully", "success");
    router.push(safeRedirectPath(route.query.redirect));
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    formError.value = getApiErrorMessage(err, "Google login failed");
    toast(formError.value, "error");
    await focusAfterPaint(() => formErrorEl.value);
  } finally {
    googleLoading.value = false;
  }
}
</script>

<template>
  <AuthPageShell title="login" variant="login" back-to="/">
    <form class="space-y-4" @submit.prevent="handleLogin">
      <BaseInput
        v-model="email"
        type="email"
        name="email"
        autocomplete="email"
        label="email"
        placeholder="you@example.com"
        required
      />
      <BaseInput
        v-model="password"
        type="password"
        name="password"
        autocomplete="current-password"
        label="password"
        placeholder="password"
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
      <BaseButton
        type="submit"
        variant="primary"
        class="w-full"
        :loading="loading"
        :disabled="!canSubmit"
      >
        {{ loading ? "signing in..." : "login" }}
      </BaseButton>
    </form>

    <div v-if="isFirebaseEnabled" class="mt-5">
      <div class="flex items-center gap-3 text-xs text-surface-mid mb-4">
        <span class="h-px flex-1 bg-surface-border" />
        <span>or</span>
        <span class="h-px flex-1 bg-surface-border" />
      </div>
      <BaseButton
        type="button"
        variant="secondary"
        class="w-full gap-2"
        :loading="googleLoading"
        @click="handleGoogleLogin"
      >
        <GoogleMarkIcon class-name="size-4" />
        {{ googleLoading ? "connecting..." : "continue with google" }}
      </BaseButton>
    </div>

    <p class="text-center text-xs text-surface-mid mt-4 space-x-3">
      <RouterLink to="/register" class="nav-link underline underline-offset-4">
        create account
      </RouterLink>
      <span>·</span>
      <RouterLink to="/forgot-password" class="nav-link underline underline-offset-4">
        forgot password?
      </RouterLink>
    </p>
  </AuthPageShell>
</template>
