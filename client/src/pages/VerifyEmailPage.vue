<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import AuthPageShell from "@/components/auth/AuthPageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { api } from "@/composables/useApi";
import { getApiErrorMessage } from "@/types/api";
import { consumeQueryParams } from "@/utils/consumeQueryParams";

const route = useRoute();
const router = useRouter();

const status = ref<"loading" | "success" | "error">("loading");
const message = ref("");

onMounted(async () => {
  const { token } = await consumeQueryParams(router, route.path, route.query, ["token"]);
  if (typeof token !== "string" || !token.trim()) {
    status.value = "error";
    message.value = "Missing verification token.";
    return;
  }

  try {
    const { data } = await api.post<{ message: string }>("/auth/verify", {
      token,
    });
    status.value = "success";
    message.value = data.message;
  } catch (err) {
    status.value = "error";
    message.value = getApiErrorMessage(err, "Verification failed.");
  }
});
</script>

<template>
  <AuthPageShell
    title="email verification"
    max-width="md"
    :back-to="status === 'error' ? '/login' : undefined"
    title-align="center"
  >
    <div
      :role="status === 'error' ? 'alert' : 'status'"
      :aria-live="status === 'error' ? 'assertive' : 'polite'"
      :aria-busy="status === 'loading'"
      class="text-sm text-center"
      :class="{
        'text-surface-mid': status === 'loading',
        'text-status-success': status === 'success',
        'text-status-error': status === 'error',
      }"
    >
      <p v-if="status === 'loading'">Verifying your email...</p>
      <p v-else>{{ message }}</p>
    </div>

    <BaseButton
      v-if="status !== 'loading'"
      type="button"
      variant="primary"
      size="lg"
      class="w-full mt-4"
      @click="router.push('/login')"
    >
      continue to login
    </BaseButton>
  </AuthPageShell>
</template>
