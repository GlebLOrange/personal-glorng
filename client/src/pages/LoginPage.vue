<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { useNotify } from "@/composables/useNotify";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const { toast } = useNotify();

function loginRedirectTarget(): string {
  const redirect = route.query.redirect;
  if (typeof redirect !== "string" || !redirect.startsWith("/") || redirect.startsWith("//")) {
    return "/admin";
  }
  return redirect;
}

const email = ref("");
const password = ref("");
const loading = ref(false);

async function handleLogin(): Promise<void> {
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    toast("Logged in successfully", "success");
    router.push(loginRedirectTarget());
  } catch (err) {
    console.error(err);
    toast("Invalid credentials", "error");
  } finally {
    loading.value = false;
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
        <BaseInput v-model="email" type="email" label="Email" placeholder="admin@glorng.dev" />
        <BaseInput v-model="password" type="password" label="Password" placeholder="••••••••" />
        <BaseButton variant="primary" class="w-full" :disabled="loading">
          {{ loading ? "Authenticating..." : "Login" }}
        </BaseButton>
      </form>

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
