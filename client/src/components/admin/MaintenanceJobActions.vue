<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, useTemplateRef } from "vue";

import TurnstileWidget from "@/components/admin/TurnstileWidget.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import { api } from "@/composables/useApi";
import { getApiErrorMessage } from "@/types/api";

type MaintenanceStatus = "idle" | "running" | "ok" | "failed";
export type MaintenanceJob = "backup" | "stale" | "sync" | "cleanup" | "seed";

interface MaintenanceInfo {
  site_key: string;
  enabled: boolean;
  host_jobs_ready: boolean;
  status: MaintenanceStatus;
  detail: string;
  job: string;
  report: string;
}

const props = withDefaults(
  defineProps<{
    /** hub: omit when Turnstile is off. page: show setup hints. */
    mode?: "hub" | "page";
  }>(),
  { mode: "page" },
);

const JOBS: {
  id: MaintenanceJob;
  label: string;
  needsHost: boolean;
  danger: boolean;
}[] = [
  { id: "backup", label: "backup", needsHost: true, danger: true },
  { id: "stale", label: "stale check", needsHost: true, danger: false },
  { id: "sync", label: "calendar sync", needsHost: false, danger: false },
  { id: "cleanup", label: "cleanup", needsHost: false, danger: true },
  { id: "seed", label: "seed demo data", needsHost: false, danger: true },
];

const CONFIRM_COPY: Record<MaintenanceJob, string> = {
  backup:
    "this starts the host backup and migrate script. confirm only if you intend to run it now.",
  stale: "this checks whether LAST_SUCCESS is fresh. confirm only if you intend to run it now.",
  sync: "this drains one calendar sync batch (max 10 items). confirm to run now.",
  cleanup:
    "this deletes old tasks, expired file shares, and old health results. confirm to run now.",
  seed: "this wipes and refills mock demo data. never use on production without an explicit override. confirm to run now.",
};

const info = ref<MaintenanceInfo | null>(null);
const pendingJob = ref<MaintenanceJob | null>(null);
const token = ref("");
const loadError = ref("");
const actionError = ref("");
const statusMessage = ref("");
const confirmOpen = ref(false);
const starting = ref(false);
const loaded = ref(false);
const turnstileRef = useTemplateRef<InstanceType<typeof TurnstileWidget>>("turnstile");

let pollTimer: ReturnType<typeof setInterval> | null = null;

const regionBusy = computed(() => info.value?.status === "running" || starting.value);

const captchaReady = computed(() => Boolean(token.value));

const showPanel = computed(() => {
  if (!loaded.value) return props.mode === "page";
  if (props.mode === "hub") return Boolean(info.value?.enabled && info.value.site_key);
  return true;
});

const confirmTitle = computed(() => (pendingJob.value ? `run ${pendingJob.value}` : "run job"));
const confirmBody = computed(() => (pendingJob.value ? CONFIRM_COPY[pendingJob.value] : ""));

function jobBlocked(job: (typeof JOBS)[number]): boolean {
  return Boolean(job.needsHost && info.value && !info.value.host_jobs_ready);
}

function canStartJob(job: (typeof JOBS)[number]): boolean {
  return (
    captchaReady.value &&
    Boolean(info.value?.enabled) &&
    info.value?.status !== "running" &&
    !starting.value &&
    !jobBlocked(job)
  );
}

async function loadStatus(): Promise<void> {
  try {
    const { data } = await api.get<MaintenanceInfo>("/admin/maintenance");
    info.value = data;
    if (data.detail && data.status !== "idle") {
      if (data.status === "failed") {
        actionError.value = data.detail;
        statusMessage.value = data.report || "";
      } else {
        statusMessage.value = data.report || data.detail;
        if (data.status === "ok") actionError.value = "";
      }
    }
    if (data.status === "running") startPolling();
    else stopPolling();
  } catch {
    loadError.value = "could not load maintenance status";
  } finally {
    loaded.value = true;
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

function openConfirm(job: MaintenanceJob): void {
  const meta = JOBS.find((j) => j.id === job);
  if (!meta || !canStartJob(meta)) return;
  pendingJob.value = job;
  actionError.value = "";
  confirmOpen.value = true;
}

function cancelConfirm(): void {
  confirmOpen.value = false;
  pendingJob.value = null;
}

async function confirmRun(): Promise<void> {
  if (!token.value || !pendingJob.value) return;
  const job = pendingJob.value;
  starting.value = true;
  actionError.value = "";
  try {
    const { data } = await api.post<MaintenanceInfo>("/admin/maintenance/run", {
      turnstile_token: token.value,
      job,
    });
    confirmOpen.value = false;
    pendingJob.value = null;
    token.value = "";
    turnstileRef.value?.reset();
    info.value = {
      site_key: info.value?.site_key ?? "",
      enabled: info.value?.enabled ?? false,
      host_jobs_ready: info.value?.host_jobs_ready ?? false,
      status: data.status,
      detail: data.detail,
      job: data.job || job,
      report: data.report || "",
    };
    statusMessage.value = data.detail || `${job} is running`;
    startPolling();
  } catch (err: unknown) {
    actionError.value = getApiErrorMessage(err, "maintenance failed").toLowerCase();
    token.value = "";
    turnstileRef.value?.reset();
    confirmOpen.value = false;
    pendingJob.value = null;
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
  <div v-if="showPanel" class="space-y-4" :aria-busy="regionBusy || undefined">
    <h2 v-if="mode === 'hub'" class="text-meta uppercase tracking-wider">jobs</h2>

    <p v-if="loadError" class="text-sm text-status-error" role="alert">{{ loadError }}</p>

    <p
      v-else-if="mode === 'page' && info && !info.enabled"
      class="rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-sm lowercase text-surface-sage"
      role="status"
    >
      not available in this deploy. set turnstile keys. for backup/stale also set
      <code class="text-surface-mid">DB_MAINTENANCE_*</code>
      on a host api process, or use
      <code class="text-surface-mid">make backup</code>.
    </p>

    <div v-if="info?.site_key" class="space-y-3">
      <TurnstileWidget
        ref="turnstile"
        :site-key="info.site_key"
        @update:token="token = $event"
        @error="onCaptchaError"
      />

      <div class="flex flex-wrap gap-2">
        <BaseButton
          v-for="job in JOBS"
          :key="job.id"
          :variant="job.danger ? 'delete' : 'secondary'"
          :danger="job.danger"
          size="sm"
          :disabled="!canStartJob(job)"
          :loading="starting && pendingJob === job.id"
          @click="openConfirm(job.id)"
        >
          {{ job.label }}
          <span v-if="jobBlocked(job)" class="ml-1 text-xs opacity-70">
            (host script not ready)
          </span>
        </BaseButton>
      </div>

      <p
        v-if="info && !info.host_jobs_ready"
        class="text-sm lowercase text-surface-sage"
        role="status"
      >
        backup and stale check need the host maintenance script.
      </p>
    </div>

    <p
      v-else-if="mode === 'page' && info && !info.site_key"
      class="text-sm lowercase text-surface-sage"
      role="status"
    >
      turnstile site key is not configured.
    </p>

    <p v-if="statusMessage" class="text-sm lowercase text-surface-sage" role="status">
      {{ statusMessage }}
    </p>
    <p
      v-if="info?.report && info.status !== 'running'"
      class="text-sm lowercase text-surface-mid"
      role="status"
    >
      report: {{ info.report }}
    </p>
    <p v-if="actionError" class="text-sm lowercase text-status-error" role="alert">
      {{ actionError }}
    </p>

    <ConfirmDialog
      :open="confirmOpen"
      :title="confirmTitle"
      confirm-label="run job"
      loading-label="running…"
      :loading="starting"
      danger
      @confirm="confirmRun"
      @cancel="cancelConfirm"
    >
      <p>{{ confirmBody }}</p>
    </ConfirmDialog>
  </div>
</template>
