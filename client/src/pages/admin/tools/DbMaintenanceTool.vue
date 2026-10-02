<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, useTemplateRef } from "vue";

import TurnstileWidget from "@/components/admin/TurnstileWidget.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import { api } from "@/composables/useApi";
import { getApiErrorMessage } from "@/types/api";

type MaintenanceStatus = "idle" | "running" | "ok" | "failed";

interface MaintenanceInfo {
  site_key: string;
  enabled: boolean;
  status: MaintenanceStatus;
  detail: string;
}

const info = ref<MaintenanceInfo | null>(null);
const token = ref("");
const loadError = ref("");
const actionError = ref("");
const statusMessage = ref("");
const confirmOpen = ref(false);
const starting = ref(false);
const turnstileRef = useTemplateRef<InstanceType<typeof TurnstileWidget>>("turnstile");

let pollTimer: ReturnType<typeof setInterval> | null = null;

const canStart = computed(
  () =>
    Boolean(token.value) &&
    Boolean(info.value?.enabled) &&
    info.value?.status !== "running" &&
    !starting.value,
);

const regionBusy = computed(() => info.value?.status === "running" || starting.value);

async function loadStatus(): Promise<void> {
  try {
    const { data } = await api.get<MaintenanceInfo>("/admin/maintenance");
    info.value = data;
    if (data.detail && data.status !== "idle") {
      if (data.status === "failed") {
        actionError.value = data.detail;
        statusMessage.value = "";
      } else {
        statusMessage.value = data.detail;
        if (data.status === "ok") actionError.value = "";
      }
    }
    if (data.status === "running") startPolling();
    else stopPolling();
  } catch {
    loadError.value = "could not load maintenance status";
  }
}

function startPolling(): void {
  if (pollTimer) return;
  pollTimer = setInterval(() => {
    void loadStatus();
  }, 2000);
}

function stopPolling(): void {
  if (!pollTimer) return;
  clearInterval(pollTimer);
  pollTimer = null;
}

function onCaptchaError(message: string): void {
  actionError.value = message;
  token.value = "";
}

function openConfirm(): void {
  if (!canStart.value) return;
  actionError.value = "";
  confirmOpen.value = true;
}

function cancelConfirm(): void {
  confirmOpen.value = false;
}

async function confirmRun(): Promise<void> {
  if (!token.value) return;
  starting.value = true;
  actionError.value = "";
  try {
    const { data } = await api.post<MaintenanceInfo>("/admin/maintenance/run", {
      turnstile_token: token.value,
    });
    confirmOpen.value = false;
    token.value = "";
    turnstileRef.value?.reset();
    info.value = {
      site_key: info.value?.site_key ?? "",
      enabled: info.value?.enabled ?? false,
      status: data.status,
      detail: data.detail,
    };
    statusMessage.value = data.detail || "maintenance is running";
    startPolling();
  } catch (err: unknown) {
    actionError.value = getApiErrorMessage(err, "maintenance failed").toLowerCase();
    token.value = "";
    turnstileRef.value?.reset();
    confirmOpen.value = false;
  } finally {
    starting.value = false;
  }
}

onMounted(() => {
  void loadStatus();
});

onUnmounted(() => {
  stopPolling();
});
</script>

<template>
  <AdminPageLayout hub="admin" title="db maintenance" back-to="/admin">
    <div class="space-y-4" :aria-busy="regionBusy || undefined">
      <p class="text-sm lowercase text-surface-sage">
        backs up mongo, redis, and media, verifies the archive, then runs migrations. a second run
        waits until this one finishes.
      </p>

      <p v-if="loadError" class="text-sm text-status-error" role="alert">{{ loadError }}</p>

      <p
        v-else-if="info && !info.enabled"
        class="rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm lowercase text-surface-sage"
        role="status"
      >
        not available in this deploy. use
        <code class="text-surface-mid">make backup</code>
        on the host, or set turnstile and
        <code class="text-surface-mid">DB_MAINTENANCE_*</code>
        on a host api process.
      </p>

      <div v-if="info?.site_key" class="space-y-3">
        <TurnstileWidget
          ref="turnstile"
          :site-key="info.site_key"
          @update:token="token = $event"
          @error="onCaptchaError"
        />
        <BaseButton
          variant="delete"
          danger
          :disabled="!canStart"
          :loading="starting"
          @click="openConfirm"
        >
          start maintenance
        </BaseButton>
      </div>

      <p
        v-else-if="info && !info.site_key"
        class="text-sm lowercase text-surface-sage"
        role="status"
      >
        turnstile site key is not configured.
      </p>

      <p v-if="statusMessage" class="text-sm lowercase text-surface-sage" role="status">
        {{ statusMessage }}
      </p>
      <p v-if="actionError" class="text-sm lowercase text-status-error" role="alert">
        {{ actionError }}
      </p>
    </div>

    <ConfirmDialog
      :open="confirmOpen"
      title="run database maintenance"
      confirm-label="run maintenance"
      loading-label="running…"
      :loading="starting"
      danger
      @confirm="confirmRun"
      @cancel="cancelConfirm"
    >
      <p>
        this starts the host backup and migrate script. confirm only if you intend to run it now.
      </p>
    </ConfirmDialog>
  </AdminPageLayout>
</template>
