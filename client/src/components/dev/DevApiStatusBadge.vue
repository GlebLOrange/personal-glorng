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

/** Keep chip width stable across poll states. */
const fitLabels = Object.values(appearance).map((entry) => entry.label);

async function poll(): Promise<void> {
  try {
    const res = await api.get("/health", {
      timeout: 5_000,
      // ponytail: skip auth refresh loop for anonymous liveness probe
      validateStatus: (code) => code >= 200 && code < 500,
    });
    // 4xx (accepted by validateStatus) is odd, not down — down is network/5xx via catch
    if (res.status !== 200) {
      status.value = "unexpected";
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
    class="print:hidden"
    aria-live="polite"
    :aria-label="`Development API status: ${appearance[status].label}`"
  >
    <StatusBadge
      :label="appearance[status].label"
      :class-name="appearance[status].className"
      :fit-labels="fitLabels"
    />
  </p>
</template>
