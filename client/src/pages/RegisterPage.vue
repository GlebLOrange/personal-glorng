<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
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
const formError = ref("");

const strength = computed(() => passwordStrength(password.value));
const passwordsMatch = computed(
  () => !!passwordConfirm.value && password.value === passwordConfirm.value,
);
const canSubmit = computed(
  () =>
    !!email.value.trim() &&
    strength.value.valid &&
    passwordsMatch.value &&
    acceptTerms.value &&
    !loading.value,
);

async function handleRegister(): Promise<void> {
  if (!canSubmit.value) return;
  loading.value = true;
  formError.value = "";
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
    formError.value = getApiErrorMessage(err, "Registration failed");
    toast(formError.value, "error");
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

      <div v-if="submitted" class="text-center space-y-4" role="status">
        <p class="text-surface-mid text-sm">
          We sent a verification link to <strong class="text-surface-light">{{ email }}</strong
          >. Open it to activate your account, then log in.
        </p>
        <BaseButton type="button" variant="primary" class="w-full" @click="router.push('/login')">
          go to login
        </BaseButton>
      </div>

      <form v-else class="space-y-4" @submit.prevent="handleRegister">
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
          v-model="displayName"
          type="text"
          name="name"
          autocomplete="nickname"
          label="display name"
          placeholder="optional"
        />
        <BaseInput
          v-model="timezone"
          type="text"
          name="timezone"
          autocomplete="off"
          label="timezone"
          placeholder="Europe/Warsaw"
        />
        <BaseInput
          v-model="password"
          type="password"
          name="password"
          autocomplete="new-password"
          label="password"
          placeholder="password"
          aria-describedby="register-password-strength"
          required
        />
        <p
          id="register-password-strength"
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
        <label class="flex items-start gap-3 min-h-11 text-xs text-surface-mid cursor-pointer">
          <input
            v-model="acceptTerms"
            type="checkbox"
            class="mt-1 h-4 w-4 accent-accent-blue focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
            required
          />
          <span>
            I accept the
            <RouterLink to="/privacy" class="nav-link inline">privacy policy</RouterLink>
            and terms of use
          </span>
        </label>
        <p v-if="formError" class="text-xs text-status-error" role="alert">{{ formError }}</p>
        <BaseButton type="submit" variant="primary" class="w-full" :loading="loading" :disabled="!canSubmit">
          {{ loading ? "creating account..." : "create account" }}
        </BaseButton>
      </form>

      <p class="text-center text-xs text-surface-mid mt-6">
        Already have an account?
        <RouterLink to="/login" class="nav-link inline">log in</RouterLink>
      </p>

      <p class="flex justify-center mt-4">
        <BackLink to="/login" />
      </p>
    </div>
  </div>
</template>
