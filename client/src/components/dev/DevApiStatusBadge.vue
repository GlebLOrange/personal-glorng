<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";

import { api } from "@/composables/useApi";
import { parseHealthStatusPayload, type HealthUiStatus } from "@/utils/parseHealthStatus";

const status = ref<HealthUiStatus | "loading">("loading");
const POLL_MS = 30_000;
let timer: ReturnType<typeof setInterval> | undefined;

async function poll(): Promise<void> {
  try {
    const res = await api.get<{ status: string }>("/health", {
      timeout: 5_000,
      // ponytail: skip auth refresh loop for anonymous liveness probe
      validateStatus: (code) => code >= 200 && code < 500,
    });
    status.value = parseHealthStatusPayload(res.data);
  } catch {
    status.value = "unreachable";
  }
}

onMounted(() => {
  void poll();
  timer = setInterval(() => void poll(), POLL_MS);
});

onUnmounted(() => {
  if (timer !== undefined) {
    clearInterval(timer);
  }
});

const label = {
  loading: "API …",
  ok: "API ok",
  unexpected: "API odd",
  unreachable: "API down",
} as const;
</script>

<template>
  <p
    class="fixed bottom-2 right-2 z-40 rounded-md border border-surface-border bg-surface/90 px-2 py-1 text-xs text-muted-foreground shadow-sm backdrop-blur-sm"
    aria-live="polite"
    :aria-label="`Development API status: ${label[status]}`"
  >
    {{ label[status] }}
  </p>
</template>
