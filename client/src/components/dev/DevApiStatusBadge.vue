<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";

import StatusBadge from "@/components/ui/StatusBadge.vue";
import { api } from "@/composables/useApi";
import { familyBadgeClass } from "@/constants/httpStatusColors";
import { parseHealthStatusPayload, type HealthUiStatus } from "@/utils/parseHealthStatus";

type BadgeStatus = HealthUiStatus | "loading" | "unreachable";

const status = ref<BadgeStatus>("loading");
const POLL_MS = 30_000;
let timer: ReturnType<typeof setInterval> | undefined;

const appearance: Record<BadgeStatus, { label: string; className: string }> = {
  loading: { label: "API …", className: familyBadgeClass("1xx") },
  ok: { label: "API ok", className: familyBadgeClass("2xx") },
  unexpected: { label: "API odd", className: familyBadgeClass("3xx") },
  unreachable: { label: "API down", className: familyBadgeClass("5xx") },
};

async function poll(): Promise<void> {
  try {
    const res = await api.get("/health", {
      timeout: 5_000,
      // ponytail: skip auth refresh loop for anonymous liveness probe
      validateStatus: (code) => code >= 200 && code < 500,
    });
    if (res.status !== 200) {
      status.value = "unreachable";
      return;
    }
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
</script>

<template>
  <p
    class="fixed bottom-[max(0.5rem,env(safe-area-inset-bottom))] right-2 z-40 print:hidden"
    aria-live="polite"
  >
    <StatusBadge
      :label="appearance[status].label"
      :class-name="appearance[status].className"
    />
  </p>
</template>
