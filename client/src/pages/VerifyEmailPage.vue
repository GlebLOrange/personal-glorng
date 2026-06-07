<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import BaseButton from "@/components/ui/BaseButton.vue";
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
    const { data } = await api.get<{ message: string }>("/auth/verify", {
      params: { token },
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

      <p v-if="status === 'loading'" class="text-surface-mid text-sm">Verifying your email...</p>
      <p v-else class="text-sm" :class="status === 'success' ? 'text-green-400' : 'text-red-400'">
        {{ message }}
      </p>

      <BaseButton
        v-if="status !== 'loading'"
        variant="primary"
        class="w-full"
        @click="router.push('/login')"
      >
        Continue to login
      </BaseButton>
    </div>
  </div>
</template>
