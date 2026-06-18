<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BaseButton from "@/components/ui/BaseButton.vue";
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

async function handleLogin(): Promise<void> {
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    toast("Logged in successfully", "success");
    router.push(safeRedirectPath(route.query.redirect));
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast(getApiErrorMessage(err, "Invalid email or password"), "error");
  } finally {
    loading.value = false;
  }
}

async function handleGoogleLogin(): Promise<void> {
  googleLoading.value = true;
  try {
    await auth.loginWithGoogle();
    toast("Logged in successfully", "success");
    router.push(safeRedirectPath(route.query.redirect));
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast(getApiErrorMessage(err, "Google login failed"), "error");
  } finally {
    googleLoading.value = false;
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-6">
    <div class="w-full max-w-sm">
      <h1 class="text-2xl font-bold text-surface-light mb-8 text-center">
        <span class="accent-gradient">€ login</span>
      </h1>

      <form class="space-y-4" @submit.prevent="handleLogin">
        <BaseInput v-model="email" type="email" label="Email" placeholder="you@example.com" />
        <BaseInput v-model="password" type="password" label="Password" placeholder="••••••••••••" />
        <BaseButton variant="primary" class="w-full" :disabled="loading">
          {{ loading ? "Authenticating..." : "Login" }}
        </BaseButton>
      </form>

      <div v-if="isFirebaseEnabled" class="mt-5">
        <div class="flex items-center gap-3 text-xs text-surface-mid mb-4">
          <span class="h-px flex-1 bg-surface-border" />
          <span>or</span>
          <span class="h-px flex-1 bg-surface-border" />
        </div>
        <BaseButton
          variant="secondary"
          class="w-full flex items-center justify-center gap-2"
          :disabled="googleLoading"
          @click="handleGoogleLogin"
        >
          <span class="font-data text-sm" aria-hidden="true">G</span>
          {{ googleLoading ? "Connecting..." : "Continue with Google" }}
        </BaseButton>
      </div>

      <p class="text-center text-xs text-surface-mid mt-4 space-x-3">
        <RouterLink to="/register" class="hover:text-accent-blue transition-colors">
          Create account
        </RouterLink>
        <span>·</span>
        <RouterLink to="/forgot-password" class="hover:text-accent-blue transition-colors">
          Forgot password?
        </RouterLink>
      </p>

      <p class="text-center text-xs text-surface-mid mt-4">
        <RouterLink to="/" class="hover:text-accent-blue transition-colors">
          &larr; Back to portfolio
        </RouterLink>
      </p>
    </div>
  </div>
</template>
