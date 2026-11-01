<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminTabBar from "@/components/admin/AdminTabBar.vue";
import PageShell from "@/components/layout/PageShell.vue";
import PlusIcon from "@/components/icons/PlusIcon.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import SyncIcon from "@/components/icons/SyncIcon.vue";
import TaskCreateModal from "@/components/tasks/TaskCreateModal.vue";
import TaskDetailModal from "@/components/tasks/TaskDetailModal.vue";
import TasksCalendarPanel from "@/components/tasks/TasksCalendarPanel.vue";
import TasksIntakesPanel from "@/components/tasks/TasksIntakesPanel.vue";
import TasksListPanel from "@/components/tasks/TasksListPanel.vue";
import TasksSyncPanel from "@/components/tasks/TasksSyncPanel.vue";
import SearchInput from "@/components/ui/SearchInput.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { statusBadgeClass } from "@/constants/filterColors";
import { effectiveSearchQuery } from "@/constants/search";
import { FILTER_MENU_ROW_CLASS } from "@/constants/toolbarPopover";
import { usePermissions } from "@/composables/usePermissions";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { useTasks } from "@/composables/useTasks";

import type { AdminTabIcon } from "@/components/admin/AdminTabBar.vue";
import type { HttpStatusFamily } from "@/constants/httpStatusColors";

type Tab = "queue" | "calendar" | "intakes" | "sync";

const TASK_TABS: {
  id: Tab;
  label: string;
  icon: AdminTabIcon;
  family?: HttpStatusFamily;
}[] = [
  { id: "queue", label: "queue", icon: "queue" },
  { id: "calendar", label: "calendar", icon: "calendar" },
  { id: "intakes", label: "intakes", icon: "intakes" },
  { id: "sync", label: "sync", icon: "sync", family: "5xx" },
];

function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

function todayDateKey(): string {
  const now = new Date();
  return `${now.getFullYear()}-${pad2(now.getMonth() + 1)}-${pad2(now.getDate())}`;
}

function monthRangeIso(year: number, month: number): { start: string; end: string } {
  const start = new Date(year, month, 1);
  const end = new Date(year, month + 1, 1);
  return { start: start.toISOString(), end: end.toISOString() };
}

const STATUS_FILTERS = [
  { label: "pending", value: "pending" },
  { label: "completed", value: "completed" },
  { label: "not completed", value: "not_completed" },
  { label: "postponed", value: "postponed" },
  { label: "cancelled", value: "cancelled" },
] as const;

const route = useRoute();
const router = useRouter();
const activeTab = ref<Tab>("queue");
const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");
const now = new Date();
const calendarYear = ref(now.getFullYear());
const calendarMonth = ref(now.getMonth());
const selectedDate = ref(todayDateKey());

const { isSuperuser } = usePermissions();

const {
  DEFAULT_FILTER_STATUS,
  tasks,
  calendarTasks,
  calendarTruncated,
  syncQueue,
  intakes,
  selectedTask,
  stats,
  filterStatus,
  searchQuery,
  whenAriaSort,
  whenIndicator,
  page,
  showCreateForm,
  createForm,
  createErrors,
  listLoading,
  calendarLoading,
  intakesLoading,
  syncLoading,
  detailLoading,
  saving,
  statusUpdating,
  rescheduling,
  hasNextPage,
  hasPreviousPage,
  hasNextIntakePage,
  hasPreviousIntakePage,
  hasNextSyncPage,
  hasPreviousSyncPage,
  intakePage,
  syncPage,
  totalPages,
  intakeTotalPages,
  syncTotalPages,
  total,
  intakeTotal,
  syncTotal,
  loadTasks,
  loadCalendarMonth,
  loadIntakes,
  loadSyncQueue,
  loadStats,
  openDetail,
  closeDetail,
  retrySync,
  processSyncQueueNow,
  pingBot,
  pingingBot,
  updateTaskStatus,
  rescheduleTask,
  openCreate,
  createTask,
  goToPage,
  goToIntakePage,
  goToSyncPage,
  toggleWhenSort,
} = useTasks();

const activeFilterLabel = computed(
  () => STATUS_FILTERS.find((chip) => chip.value === filterStatus.value)?.label,
);

function parseTaskTab(value: unknown): Tab | null {
  return typeof value === "string" && TASK_TABS.some((item) => item.id === value)
    ? (value as Tab)
    : null;
}

async function reloadCalendar(): Promise<void> {
  const { start, end } = monthRangeIso(calendarYear.value, calendarMonth.value);
  await loadCalendarMonth(start, end);
}

function switchTab(tab: string): void {
  if (!TASK_TABS.some((item) => item.id === tab)) return;
  activeTab.value = tab as Tab;
  const query = { ...route.query, tab } as Record<string, string>;
  if (tab === "calendar") {
    query.date = selectedDate.value;
  }
  void router.replace({ query });
  if (tab === "intakes") void loadIntakes();
  if (tab === "sync") void loadSyncQueue();
  if (tab === "calendar") void reloadCalendar();
}

function selectCalendarDate(date: string): void {
  selectedDate.value = date;
  void router.replace({ query: { ...route.query, tab: "calendar", date } });
  const [y, m] = date.split("-").map(Number);
  if (y !== calendarYear.value || m - 1 !== calendarMonth.value) {
    calendarYear.value = y;
    calendarMonth.value = m - 1;
    void reloadCalendar();
  }
}

function shiftCalendarMonth(delta: number): void {
  const next = new Date(calendarYear.value, calendarMonth.value + delta, 1);
  calendarYear.value = next.getFullYear();
  calendarMonth.value = next.getMonth();
  selectedDate.value = `${calendarYear.value}-${pad2(calendarMonth.value + 1)}-01`;
  void router.replace({
    query: { ...route.query, tab: "calendar", date: selectedDate.value },
  });
  void reloadCalendar();
}

async function onUpdateStatus(status: Parameters<typeof updateTaskStatus>[1]): Promise<void> {
  if (!selectedTask.value) return;
  await updateTaskStatus(selectedTask.value.id, status);
  if (activeTab.value === "calendar") await reloadCalendar();
}

async function onReschedule(scheduledAtLocal: string): Promise<void> {
  if (!selectedTask.value) return;
  await rescheduleTask(selectedTask.value.id, scheduledAtLocal);
  if (activeTab.value === "calendar") await reloadCalendar();
}

function setStatusFilter(status: string): void {
  filterStatus.value = status;
  filterDropdownRef.value?.close();
}

function clearFilters(): void {
  filterStatus.value = DEFAULT_FILTER_STATUS;
  searchQuery.value = "";
  filterDropdownRef.value?.close();
}

const hasActiveFilters = computed(
  () =>
    filterStatus.value !== DEFAULT_FILTER_STATUS ||
    Boolean(effectiveSearchQuery(searchQuery.value)),
);

/** Calendar create is blocked for local dates before today. */
const selectedDateIsPast = computed(() => selectedDate.value < todayDateKey());

const createDisabled = computed(() => {
  if (activeTab.value === "calendar") {
    return calendarLoading.value || selectedDateIsPast.value;
  }
  return listLoading.value;
});

function onCreateClick(): void {
  if (activeTab.value === "calendar") {
    if (selectedDateIsPast.value) return;
    openCreate(selectedDate.value);
    return;
  }
  openCreate();
}

function onFailedSyncs(): void {
  filterDropdownRef.value?.close();
  switchTab("sync");
}

watch(activeTab, (tab) => {
  if (tab !== "queue") filterDropdownRef.value?.close();
});

useScrollListFingerprint(
  () =>
    `${activeTab.value}:${filterStatus.value}:${searchQuery.value}:${page.value}:${tasks.value[0]?.id ?? ""}:${intakes.value[0]?.id ?? ""}:${syncQueue.value[0]?.id ?? ""}`,
);

onMounted(() => {
  const tab = parseTaskTab(route.query.tab);
  const dateParam = route.query.date;
  if (typeof dateParam === "string" && /^\d{4}-\d{2}-\d{2}$/.test(dateParam)) {
    selectedDate.value = dateParam;
    const [y, m] = dateParam.split("-").map(Number);
    calendarYear.value = y;
    calendarMonth.value = m - 1;
  }
  if (tab) {
    activeTab.value = tab;
    if (tab === "intakes") void loadIntakes();
    if (tab === "sync") void loadSyncQueue();
    if (tab === "calendar") void reloadCalendar();
  }
  void loadTasks();
  void loadStats();
});
</script>

<template>
  <PageShell
    title="tasks"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'tasks' }]"
    back-to="/tools"
    max-width="5xl"
    body-width="column"
    description="Telegram reminders and Google Calendar sync share this queue with the web UI."
  >
    <div class="w-full min-w-0 self-stretch">
      <div class="page-tool-actions">
        <div class="flex min-w-0 flex-wrap items-center gap-2">
          <AdminFilterDropdown
            v-show="activeTab === 'queue'"
            ref="filterDropdown"
            :has-active-filters="hasActiveFilters"
            :active-label="activeFilterLabel"
            :option-labels="STATUS_FILTERS.map((chip) => chip.label)"
            @clear="clearFilters"
          >
            <template #chips>
              <AdminFilterChip
                v-for="chip in STATUS_FILTERS"
                :key="chip.value"
                :label="chip.label"
                :active="filterStatus === chip.value"
                :color-class="statusBadgeClass(chip.value)"
                @click="setStatusFilter(chip.value)"
              />
            </template>
            <template #footer>
              <div class="mt-3 border-t border-surface-border pt-3">
                <button
                  type="button"
                  :class="[
                    FILTER_MENU_ROW_CLASS,
                    'justify-start border-transparent bg-transparent text-status-critical hover:enabled:bg-status-critical/15 focus-visible:ring-status-critical/50',
                  ]"
                  @click="onFailedSyncs"
                >
                  <SyncIcon class-name="size-3.5 shrink-0" />
                  open sync queue
                </button>
              </div>
            </template>
          </AdminFilterDropdown>

          <SearchInput
            v-if="activeTab === 'queue'"
            v-model="searchQuery"
            class="min-w-0"
            auto-width
            placeholder="search tasks"
          />

          <AdminTabBar
            flush
            panel-id-prefix="tasks-tab"
            :model-value="activeTab"
            :tabs="TASK_TABS"
            @update:model-value="switchTab"
          />

          <ToolbarPillButton
            v-if="isSuperuser"
            family="2xx"
            class="w-auto gap-1.5"
            :disabled="pingingBot"
            title="Ping Telegram todobot (getMe + DM). Does not prove polling is up."
            @click="pingBot"
          >
            <RefreshIcon class-name="size-3.5 shrink-0" />
            ping bot
          </ToolbarPillButton>

          <ToolbarPillButton
            v-if="isSuperuser"
            v-show="activeTab === 'queue' || activeTab === 'calendar'"
            action="create"
            :icon="false"
            class="w-auto"
            :disabled="createDisabled"
            :title="
              activeTab === 'calendar' && selectedDateIsPast
                ? 'Cannot create tasks on past days'
                : undefined
            "
            @click="onCreateClick"
          >
            <PlusIcon class-name="size-3.5 shrink-0" />
            task
          </ToolbarPillButton>
        </div>

        <p
          v-if="(activeTab === 'queue' || activeTab === 'calendar') && !isSuperuser"
          class="text-xs text-surface-mid"
        >
          View only — creating and status changes need superuser.
        </p>
      </div>

      <TasksListPanel
        v-if="activeTab === 'queue'"
        :tasks="tasks"
        :loading="listLoading"
        :filter-status="filterStatus"
        :when-aria-sort="whenAriaSort"
        :when-indicator="whenIndicator"
        :stats="stats"
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="hasNextPage"
        :has-previous-page="hasPreviousPage"
        @select="openDetail"
        @sort-when="toggleWhenSort"
        @failed-syncs="switchTab('sync')"
        @first-page="goToPage(1)"
        @prev-page="goToPage(page - 1)"
        @next-page="goToPage(page + 1)"
        @last-page="goToPage(totalPages)"
      />

      <TasksCalendarPanel
        v-else-if="activeTab === 'calendar'"
        :tasks="calendarTasks"
        :loading="calendarLoading"
        :truncated="calendarTruncated"
        :year="calendarYear"
        :month="calendarMonth"
        :selected-date="selectedDate"
        @prev-month="shiftCalendarMonth(-1)"
        @next-month="shiftCalendarMonth(1)"
        @select-date="selectCalendarDate"
        @select-task="openDetail"
      />

      <TasksIntakesPanel
        v-else-if="activeTab === 'intakes'"
        :intakes="intakes"
        :loading="intakesLoading"
        :total="intakeTotal"
        :page="intakePage"
        :total-pages="intakeTotalPages"
        :has-next-page="hasNextIntakePage"
        :has-previous-page="hasPreviousIntakePage"
        @first-page="goToIntakePage(1)"
        @prev-page="goToIntakePage(intakePage - 1)"
        @next-page="goToIntakePage(intakePage + 1)"
        @last-page="goToIntakePage(intakeTotalPages)"
      />

      <TasksSyncPanel
        v-else-if="activeTab === 'sync'"
        :items="syncQueue"
        :loading="syncLoading"
        :can-mutate="isSuperuser"
        :total="syncTotal"
        :page="syncPage"
        :total-pages="syncTotalPages"
        :has-next-page="hasNextSyncPage"
        :has-previous-page="hasPreviousSyncPage"
        @retry="retrySync"
        @sync-now="processSyncQueueNow"
        @first-page="goToSyncPage(1)"
        @prev-page="goToSyncPage(syncPage - 1)"
        @next-page="goToSyncPage(syncPage + 1)"
        @last-page="goToSyncPage(syncTotalPages)"
      />

      <TaskCreateModal
        v-if="isSuperuser"
        v-model:form="createForm"
        :open="showCreateForm"
        :saving="saving"
        :errors="createErrors"
        @submit="createTask"
        @close="showCreateForm = false"
      />

      <TaskDetailModal
        :open="selectedTask !== null"
        :task="selectedTask"
        :loading="detailLoading"
        :can-mutate="isSuperuser"
        :status-updating="statusUpdating"
        :rescheduling="rescheduling"
        @close="closeDetail"
        @retry-sync="retrySync"
        @update-status="onUpdateStatus"
        @reschedule="onReschedule"
      />
    </div>
  </PageShell>
</template>
