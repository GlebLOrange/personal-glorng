<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";

const route = useRoute();
const router = useRouter();
const { toast } = useNotify();

const status = ref<"loading" | "success" | "error">("loading");
const message = ref("");

onMounted(async () => {
  const code = route.query.code as string | undefined;
  const state = route.query.state as string | undefined;

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
    setTimeout(() => router.push("/admin"), 2000);
  } catch (err: unknown) {
    status.value = "error";
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    message.value = msg || "Failed to link GitHub account.";
    toast(message.value, "error");
  }
});
</script>

<template>
  <div class="min-h-[80vh] flex items-center justify-center px-6">
    <div class="w-full max-w-sm text-center">
      <div v-if="status === 'loading'" class="space-y-4">
        <div class="animate-spin mx-auto h-8 w-8 border-2 border-accent-blue border-t-transparent rounded-full" />
        <p class="text-surface-mid">Linking GitHub account...</p>
      </div>

      <div v-else-if="status === 'success'" class="space-y-4">
        <p class="text-2xl">&#10003;</p>
        <p class="text-surface-light font-medium">{{ message }}</p>
        <p class="text-xs text-surface-mid">Redirecting to dashboard...</p>
      </div>

      <div v-else class="space-y-4">
        <p class="text-2xl">&#10007;</p>
        <p class="text-surface-light font-medium">{{ message }}</p>
        <p class="text-xs text-surface-mid">
          <RouterLink to="/admin" class="hover:text-accent-blue transition-colors">
            &larr; Back to dashboard
          </RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
