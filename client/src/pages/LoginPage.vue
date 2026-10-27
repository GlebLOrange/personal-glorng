<script setup lang="ts">
import { computed, ref, useTemplateRef } from "vue";
import { useRoute, useRouter } from "vue-router";

import AuthPageShell from "@/components/auth/AuthPageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { useNotify } from "@/composables/useNotify";
import { EMAIL_FORMAT_HINT, isValidEmail } from "@/constants/contactMeta";
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
const formError = ref("");
const formErrorEl = useTemplateRef<HTMLElement>("formErrorAlert");

const emailTone = computed<"error" | undefined>(() => {
  if (!email.value.trim()) return undefined;
  return isValidEmail(email.value) ? undefined : "error";
});

const emailError = computed(() => (emailTone.value === "error" ? EMAIL_FORMAT_HINT : undefined));

const canSubmit = computed(() => isValidEmail(email.value) && !!password.value && !loading.value);

/** Map opaque reserved-TLD / special-use API detail into a clear login hint. */
function friendlyLoginError(raw: string): string {
  if (/special-use|reserved\s+name|reserved\s+TLD|\.test\b/i.test(raw)) {
    return "That email domain can't be used for sign-in. Use a real inbox address.";
  }
  return raw;
}

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
    formError.value = friendlyLoginError(getApiErrorMessage(err, "Invalid email or password"));
    toast(formError.value, "error");
    await focusAfterPaint(() => formErrorEl.value);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <AuthPageShell title="login" variant="login" back-to="/">
    <p class="text-sm text-surface-mid">
      Operator sign-in for this site.
      <RouterLink to="/" class="nav-link underline-offset-4">Back to the portfolio</RouterLink>.
    </p>
    <form class="space-y-4" @submit.prevent="handleLogin">
      <BaseInput
        v-model="email"
        type="email"
        name="email"
        autocomplete="email"
        placeholder="email@example.com"
        aria-label="email"
        :tone="emailTone"
        :error="emailError"
        required
      />
      <BaseInput
        v-model="password"
        type="password"
        name="password"
        autocomplete="current-password"
        placeholder="password"
        aria-label="password"
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
        {{ loading ? "signing in…" : "login" }}
      </BaseButton>
    </form>

    <p class="text-center text-xs text-surface-mid mt-4">
      <RouterLink to="/forgot-password" class="nav-link underline-offset-4">
        forgot password?
      </RouterLink>
    </p>
  </AuthPageShell>
</template>
