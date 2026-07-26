<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import AuthPageShell from "@/components/auth/AuthPageShell.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { getApiErrorMessage } from "@/types/api";
import { consumeQueryParams } from "@/utils/consumeQueryParams";

const route = useRoute();
const router = useRouter();
const { toast } = useNotify();

const status = ref<"loading" | "success" | "error">("loading");
const message = ref("");
let redirectTimer: ReturnType<typeof setTimeout> | null = null;

onMounted(async () => {
  const { code, state } = await consumeQueryParams(router, route.path, route.query, [
    "code",
    "state",
  ]);

  if (!code) {
    status.value = "error";
    message.value = "Missing authorization code from GitHub.";
    return;
  }

  try {
    const { data } = await api.post<{ github_username: string; message: string }>(
      "/auth/github/callback",
      { code, state: state ?? "" },
    );
    status.value = "success";
    message.value = `Connected as ${data.github_username}`;
    toast(data.message, "success");
    redirectTimer = setTimeout(() => router.push("/admin"), 2000);
  } catch (err: unknown) {
    status.value = "error";
    message.value = getApiErrorMessage(err, "Failed to link GitHub account.");
  }
});

onUnmounted(() => {
  if (redirectTimer) clearTimeout(redirectTimer);
});
</script>

<template>
  <AuthPageShell title="" :back-to="status === 'error' ? '/admin' : undefined">
    <div
      class="text-center"
      role="status"
      aria-live="polite"
      :aria-busy="status === 'loading'"
    >
      <div v-if="status === 'loading'" class="space-y-4">
        <div
          class="animate-spin mx-auto h-8 w-8 border-2 border-accent-blue border-t-transparent rounded-full"
          aria-hidden="true"
        />
        <p class="text-surface-mid">Linking GitHub account...</p>
      </div>

      <div v-else-if="status === 'success'" class="space-y-4">
        <p class="text-2xl" aria-hidden="true">&#10003;</p>
        <p class="text-surface-light font-medium">{{ message }}</p>
        <p class="text-xs text-surface-mid">Redirecting to admin…</p>
      </div>

      <div v-else class="space-y-4" role="alert">
        <p class="text-2xl" aria-hidden="true">&#10007;</p>
        <p class="text-surface-light font-medium">{{ message }}</p>
      </div>
    </div>
  </AuthPageShell>
</template>
