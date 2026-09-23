<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted } from "vue";

import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { httpStatusClass } from "@/constants/httpStatusColors";
import {
  HEALTH_INTERVALS,
  useHealthChecker,
  type HealthInterval,
} from "@/composables/useHealthChecker";

const HealthResponseTimeChart = defineAsyncComponent(
  () => import("@/components/charts/HealthResponseTimeChart.vue"),
);

const {
  canRead,
  canWrite,
  monitors,
  page,
  total,
  totalPages,
  selectedId,
  selected,
  chartLabels,
  chartValues,
  newUrl,
  newLabel,
  newInterval,
  listLoading,
  creating,
  checking,
  historyLoading,
  loadMonitors,
  selectMonitor,
  createMonitor,
  checkNow,
  toggleEnabled,
  updateInterval,
  deleteMonitor,
  goToPage,
} = useHealthChecker();

const hasNextPage = computed(() => page.value < totalPages.value);
const hasPreviousPage = computed(() => page.value > 1);
const canCreate = computed(
  () => Boolean(newUrl.value.trim()) && canWrite.value && !creating.value,
);

function sslDaysLeft(iso: string | null): string {
  if (!iso) return "n/a";
  const expires = new Date(iso).getTime();
  if (Number.isNaN(expires)) return "n/a";
  const days = Math.floor((expires - Date.now()) / (1000 * 60 * 60 * 24));
  if (days < 0) return `expired ${Math.abs(days)}d ago`;
  return `${days}d left`;
}

function formatMs(ms: number | null): string {
  if (ms == null) return "—";
  return `${Math.round(ms)} ms`;
}

onMounted(() => {
  void loadMonitors();
});
</script>

<template>
  <PageShell
    title="health checker"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'health checker' }]"
    back-to="/tools"
    max-width="xl"
    :narrow="false"
  >
    <form
      v-if="canWrite"
      class="mb-6 space-y-3"
      @submit.prevent="createMonitor"
    >
      <div class="flex min-w-0 flex-wrap items-center gap-2">
        <BaseInput
          v-model="newUrl"
          class="min-w-0 flex-1"
          placeholder="url (example.com or https://…)"
          aria-label="url to monitor"
        />
        <select
          v-model.number="newInterval"
          class="h-10 rounded-lg border border-surface-border bg-surface-card px-3 text-sm text-surface-fg"
          aria-label="check interval minutes"
        >
          <option v-for="mins in HEALTH_INTERVALS" :key="mins" :value="mins">
            every {{ mins }}m
          </option>
        </select>
        <ToolbarPillButton
          family="2xx"
          type="submit"
          class="shrink-0"
          :disabled="!canCreate"
        >
          {{ creating ? "adding…" : "add" }}
        </ToolbarPillButton>
      </div>
      <BaseInput
        v-model="newLabel"
        placeholder="label (optional)"
        aria-label="monitor label"
      />
    </form>

    <p v-else-if="!canRead" class="text-sm text-surface-muted">
      You need health-checker access to use this tool.
    </p>

    <div v-if="canRead" class="grid min-w-0 gap-6 lg:grid-cols-2">
      <div class="min-w-0">
        <AdminListSkeleton v-if="listLoading" label="loading monitors" />

        <template v-else>
          <ul v-if="monitors.length > 0" class="divide-y divide-surface-border">
            <li
              v-for="monitor in monitors"
              :key="monitor.id"
              class="flex min-w-0 items-start gap-3 py-3"
            >
              <button
                type="button"
                class="min-w-0 flex-1 rounded-lg text-left"
                :class="
                  selectedId === monitor.id ? 'bg-surface-muted/30 -mx-2 px-2 py-1' : ''
                "
                @click="selectMonitor(monitor.id)"
              >
                <div class="truncate text-sm font-medium text-surface-fg">
                  {{ monitor.label || monitor.url }}
                </div>
                <div
                  v-if="monitor.label"
                  class="truncate text-xs text-surface-muted"
                >
                  {{ monitor.url }}
                </div>
                <div class="mt-1 flex flex-wrap items-center gap-2 text-xs">
                  <span
                    v-if="monitor.last_status_code != null"
                    :class="httpStatusClass(monitor.last_status_code)"
                    class="rounded px-1.5 py-0.5 font-mono"
                  >
                    {{ monitor.last_status_code }}
                  </span>
                  <span
                    :class="
                      monitor.last_ok
                        ? 'text-status-success'
                        : monitor.last_ok === false
                          ? 'text-status-error'
                          : 'text-surface-muted'
                    "
                  >
                    {{
                      monitor.last_ok === true
                        ? "up"
                        : monitor.last_ok === false
                          ? "down"
                          : "pending"
                    }}
                  </span>
                  <span class="text-surface-muted">
                    {{ formatMs(monitor.last_response_ms) }}
                  </span>
                  <span v-if="!monitor.enabled" class="text-surface-muted">
                    paused
                  </span>
                </div>
              </button>
              <div
                v-if="canWrite"
                class="flex shrink-0 flex-col gap-1"
              >
                <ToolbarPillButton
                  family="1xx"
                  type="button"
                  class="!h-8 !px-2 !text-xs"
                  @click="toggleEnabled(monitor)"
                >
                  {{ monitor.enabled ? "pause" : "resume" }}
                </ToolbarPillButton>
                <ToolbarPillButton
                  family="4xx"
                  type="button"
                  class="!h-8 !px-2 !text-xs"
                  @click="deleteMonitor(monitor.id)"
                >
                  delete
                </ToolbarPillButton>
              </div>
            </li>
          </ul>

          <EmptyState v-else>
            no monitors yet. add a URL above to start checking.
          </EmptyState>

          <AdminListFooter
            v-if="monitors.length > 0"
            :total="total"
            :page="page"
            :total-pages="totalPages"
            :has-next-page="hasNextPage"
            :has-previous-page="hasPreviousPage"
            :loading="listLoading"
            item-label="monitors"
            aria-label="monitors pagination"
            @first="goToPage(1)"
            @prev="goToPage(page - 1)"
            @next="goToPage(page + 1)"
            @last="goToPage(totalPages)"
          />
        </template>
      </div>

      <div v-if="selected" class="min-w-0 space-y-4">
        <div class="space-y-1">
          <h2 class="text-base font-medium text-surface-fg">
            {{ selected.label || selected.url }}
          </h2>
          <p class="break-all text-xs text-surface-muted">{{ selected.url }}</p>
        </div>

        <dl class="grid grid-cols-2 gap-3 text-sm">
          <div>
            <dt class="text-xs text-surface-muted">HTTP status</dt>
            <dd>
              <span
                v-if="selected.last_status_code != null"
                :class="httpStatusClass(selected.last_status_code)"
                class="rounded px-1.5 py-0.5 font-mono text-xs"
              >
                {{ selected.last_status_code }}
              </span>
              <span v-else class="text-surface-muted">—</span>
            </dd>
          </div>
          <div>
            <dt class="text-xs text-surface-muted">response time</dt>
            <dd>{{ formatMs(selected.last_response_ms) }}</dd>
          </div>
          <div>
            <dt class="text-xs text-surface-muted">uptime</dt>
            <dd>
              {{
                selected.uptime_percent != null
                  ? `${selected.uptime_percent}%`
                  : "—"
              }}
            </dd>
          </div>
          <div>
            <dt class="text-xs text-surface-muted">SSL expiry</dt>
            <dd>{{ sslDaysLeft(selected.ssl_expires_at) }}</dd>
          </div>
        </dl>

        <div v-if="selected.last_error" class="text-xs text-status-error">
          {{ selected.last_error }}
        </div>

        <div>
          <h3 class="mb-1 text-xs text-surface-muted">DNS</h3>
          <ul v-if="selected.dns.length" class="space-y-0.5 font-mono text-xs">
            <li v-for="(rec, i) in selected.dns" :key="`${rec.family}-${rec.address}-${i}`">
              {{ rec.family }} {{ rec.address }}
            </li>
          </ul>
          <p v-else class="text-xs text-surface-muted">no records</p>
        </div>

        <div v-if="canWrite" class="flex flex-wrap items-center gap-2">
          <ToolbarPillButton
            family="2xx"
            type="button"
            :disabled="checking"
            @click="checkNow(selected.id)"
          >
            {{ checking ? "checking…" : "check now" }}
          </ToolbarPillButton>
          <select
            class="h-10 rounded-lg border border-surface-border bg-surface-card px-3 text-sm"
            :value="selected.interval_minutes"
            aria-label="change interval"
            @change="
              updateInterval(
                selected,
                Number(($event.target as HTMLSelectElement).value) as HealthInterval,
              )
            "
          >
            <option v-for="mins in HEALTH_INTERVALS" :key="mins" :value="mins">
              every {{ mins }}m
            </option>
          </select>
        </div>

        <div>
          <h3 class="mb-2 text-xs text-surface-muted">response time (24h)</h3>
          <AdminListSkeleton v-if="historyLoading" label="loading history" />
          <HealthResponseTimeChart
            v-else-if="chartValues.length > 0"
            :labels="chartLabels"
            :values="chartValues"
          />
          <EmptyState v-else>no history yet</EmptyState>
        </div>
      </div>

      <EmptyState v-else-if="monitors.length > 0" class="lg:col-start-2">
        select a monitor to see details and history
      </EmptyState>
    </div>
  </PageShell>
</template>
