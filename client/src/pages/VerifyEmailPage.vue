<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
import { api } from "@/composables/useApi";
import { getApiErrorMessage } from "@/types/api";

const route = useRoute();
const router = useRouter();

const status = ref<"loading" | "success" | "error">("loading");
const message = ref("");

onMounted(async () => {
  const token = route.query.token;
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
  <div class="min-h-[80vh] flex items-center justify-center px-6">
    <div class="w-full max-w-md text-center space-y-4">
      <h1 class="text-2xl font-bold text-surface-light">
        <span class="accent-gradient">email verification</span>
      </h1>

      <div
        role="status"
        aria-live="polite"
        :aria-busy="status === 'loading'"
        class="text-sm"
        :class="{
          'text-surface-mid': status === 'loading',
          'text-status-success': status === 'success',
          'text-status-error': status === 'error',
        }"
      >
        <p v-if="status === 'loading'">Verifying your email...</p>
        <p v-else>{{ message }}</p>
      </div>

      <button
        v-if="status !== 'loading'"
        type="button"
        class="cta-primary w-full"
        @click="router.push('/login')"
      >
        continue to login
      </button>

      <p v-if="status === 'error'" class="flex justify-center">
        <BackLink to="/login" />
      </p>
    </div>
  </div>
</template>
