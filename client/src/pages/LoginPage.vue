<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { isFirebaseEnabled } from "@/constants/firebase";
import { useNotify } from "@/composables/useNotify";
import { useAuthStore } from "@/stores/auth";
import { getApiErrorMessage } from "@/types/api";
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
  } finally {
    googleLoading.value = false;
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-6">
    <div class="w-full max-w-sm">
      <h1 class="text-2xl font-bold text-surface-light mb-8 text-center">
        <span class="accent-gradient">login</span>
      </h1>

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
        <p v-if="formError" class="text-xs text-status-error" role="alert">{{ formError }}</p>
        <button type="submit" class="cta-primary w-full" :disabled="!canSubmit">
          {{ loading ? "signing in..." : "login" }}
        </button>
      </form>

      <div v-if="isFirebaseEnabled" class="mt-5">
        <div class="flex items-center gap-3 text-xs text-surface-mid mb-4">
          <span class="h-px flex-1 bg-surface-border" />
          <span>or</span>
          <span class="h-px flex-1 bg-surface-border" />
        </div>
        <button
          type="button"
          class="cta-secondary w-full flex items-center justify-center gap-2"
          :disabled="googleLoading"
          @click="handleGoogleLogin"
        >
          <span class="font-data text-sm" aria-hidden="true">G</span>
          {{ googleLoading ? "connecting..." : "continue with Google" }}
        </button>
      </div>

      <p class="text-center text-xs text-surface-mid mt-4 space-x-3">
        <RouterLink to="/register" class="nav-link"> create account </RouterLink>
        <span>·</span>
        <RouterLink to="/forgot-password" class="nav-link"> forgot password? </RouterLink>
      </p>

      <p class="flex justify-center mt-4">
        <BackLink to="/" />
      </p>
    </div>
  </div>
</template>
