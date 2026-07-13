<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { useNotify } from "@/composables/useNotify";
import { useAuthStore } from "@/stores/auth";
import { getApiErrorMessage } from "@/types/api";
import { passwordStrength } from "@/utils/passwordPolicy";

const auth = useAuthStore();
const router = useRouter();
const { toast } = useNotify();

const email = ref("");
const password = ref("");
const passwordConfirm = ref("");
const displayName = ref("");
const timezone = ref(Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC");
const acceptTerms = ref(false);
const loading = ref(false);
const submitted = ref(false);

const strength = computed(() => passwordStrength(password.value));

async function handleRegister(): Promise<void> {
  loading.value = true;
  try {
    await auth.register({
      email: email.value,
      password: password.value,
      password_confirm: passwordConfirm.value,
      display_name: displayName.value.trim() || undefined,
      timezone: timezone.value,
      accept_terms: acceptTerms.value,
    });
    submitted.value = true;
    toast("Check your email to verify your account", "success");
  } catch (err) {
    toast(getApiErrorMessage(err, "Registration failed"), "error");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-6">
    <div class="w-full max-w-md">
      <h1 class="text-2xl font-bold text-surface-light mb-8 text-center">
        <span class="accent-gradient">create account</span>
      </h1>

      <div v-if="submitted" class="text-center space-y-4">
        <p class="text-surface-mid text-sm">
          We sent a verification link to <strong class="text-surface-light">{{ email }}</strong
          >. Open it to activate your account, then log in.
        </p>
        <BaseButton variant="primary" class="w-full" @click="router.push('/login')">
          Go to login
        </BaseButton>
      </div>

      <form v-else class="space-y-4" @submit.prevent="handleRegister">
        <BaseInput
          v-model="email"
          type="email"
          label="Email"
          placeholder="you@example.com"
          required
        />
        <BaseInput
          v-model="displayName"
          type="text"
          label="Display name (optional)"
          placeholder="How we greet you"
        />
        <BaseInput v-model="timezone" type="text" label="Timezone" placeholder="Europe/Warsaw" />
        <BaseInput
          v-model="password"
          type="password"
          label="Password"
          placeholder="••••••••••••"
          required
        />
        <p class="text-xs" :class="strength.valid ? 'text-status-success' : 'text-surface-mid'">
          {{ strength.message }}
        </p>
        <BaseInput
          v-model="passwordConfirm"
          type="password"
          label="Confirm password"
          placeholder="••••••••••••"
          required
        />
        <label class="flex items-start gap-2 text-xs text-surface-mid">
          <input v-model="acceptTerms" type="checkbox" class="mt-0.5" required />
          <span>
            I accept the
            <RouterLink to="/privacy" class="text-accent-blue hover:underline"
              >privacy policy</RouterLink
            >
          </span>
        </label>
        <BaseButton variant="primary" class="w-full" :disabled="loading || !strength.valid">
          {{ loading ? "Creating account..." : "Create account" }}
        </BaseButton>
      </form>

      <p class="text-center text-xs text-surface-mid mt-6">
        Already have an account?
        <RouterLink to="/login" class="text-accent-blue hover:underline">Log in</RouterLink>
      </p>
    </div>
  </div>
</template>
