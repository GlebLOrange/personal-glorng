<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef, watch } from "vue";
import { useRouter } from "vue-router";

import AdminDataRow from "@/components/admin/AdminDataRow.vue";
import AdminDataTable from "@/components/admin/AdminDataTable.vue";
import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import {
  ADMIN_SORT_HEADER_BUTTON_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TD_TITLE_CLASS,
  ADMIN_TH_CLASS,
} from "@/constants/adminDataTable";
import FeedbackDetailDrawer from "@/components/admin/FeedbackDetailDrawer.vue";
import PageShell from "@/components/layout/PageShell.vue";
import ArchiveIcon from "@/components/icons/ArchiveIcon.vue";
import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import RefreshIcon from "@/components/icons/RefreshIcon.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { feedbackStatusClass } from "@/constants/filterColors";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import type { PaginatedList } from "@/types";
import { formatDate } from "@/utils/format";
import { writeEmailDraft } from "@/utils/emailDraft";

interface FeedbackItem {
  id: number;
  email: string;
  theme: string;
  message: string;
  status: string;
  created_at: string;
}

type StatusFilter = "unread" | "read" | "archived";
type CreatedSort = "created_asc" | "created_desc";

const DEFAULT_STATUS_FILTER: StatusFilter = "unread";
const DEFAULT_SORT: CreatedSort = "created_desc";

const STATUS_FILTERS: { label: string; value: StatusFilter }[] = [
  { label: "unread", value: "unread" },
  { label: "read", value: "read" },
  { label: "archived", value: "archived" },
];

const NEXT_STATUS: Record<string, string> = {
  unread: "read",
  read: "archived",
  archived: "read",
};

const ADVANCE_STATUS_LABEL: Record<string, string> = {
  unread: "mark as read",
  read: "archive",
  archived: "unarchive",
};

const items = ref<FeedbackItem[]>([]);
const selectedItem = ref<FeedbackItem | null>(null);
const drawerOpen = ref(false);
const filter = ref<StatusFilter>(DEFAULT_STATUS_FILTER);
const sort = ref<CreatedSort>(DEFAULT_SORT);
const page = ref(1);
const total = ref(0);
const totalPages = ref(0);
const { loading, run: runLoad } = useApiAction();
const { run: runStatus } = useApiAction();
const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");
const router = useRouter();

const hasActiveFilters = computed(() => filter.value !== DEFAULT_STATUS_FILTER);
const activeFilterLabel = computed(
  () => STATUS_FILTERS.find((chip) => chip.value === filter.value)?.label,
);

function reply(item: FeedbackItem): void {
  writeEmailDraft({
    to: item.email,
    subject: `Re: ${item.theme}`,
    body: `\n\n--- Original ---\n${item.message}`,
  });
  void router.push({ name: "tool-email" });
}

function removeFromList(id: number): void {
  const idx = items.value.findIndex((item) => item.id === id);
  if (idx === -1) return;
  items.value.splice(idx, 1);
  total.value = Math.max(0, total.value - 1);
}

async function load(): Promise<void> {
  const data = await runLoad(
    async () => {
      const response = await api.get<PaginatedList<FeedbackItem>>("/feedback", {
        params: {
          page: page.value,
          per_page: ADMIN_LIST_PAGE_SIZE,
          status: filter.value,
          sort: sort.value,
        },
      });
      return response.data;
    },
    { errorMessage: "Failed to load feedback", logContext: "feedback.load" },
  );
  if (data) {
    items.value = data.items;
    total.value = data.total;
    totalPages.value = data.pages;
  }
}

function setFilter(next: StatusFilter): void {
  filter.value = next;
  page.value = 1;
  filterDropdownRef.value?.close();
}

function toggleCreatedSort(): void {
  sort.value = sort.value === "created_desc" ? "created_asc" : "created_desc";
  page.value = 1;
}

function sortIndicator(): string {
  return sort.value === "created_asc" ? " ↑" : " ↓";
}

function sortAriaSort(): "ascending" | "descending" {
  return sort.value === "created_asc" ? "ascending" : "descending";
}

function clearFilters(): void {
  filter.value = DEFAULT_STATUS_FILTER;
  page.value = 1;
  filterDropdownRef.value?.close();
}

function goToPage(nextPage: number): void {
  if (nextPage < 1) return;
  if (totalPages.value > 0 && nextPage > totalPages.value) return;
  page.value = nextPage;
}

async function setStatus(id: number, status: string): Promise<void> {
  const ok = await runStatus(
    async () => {
      await api.patch(`/feedback/${id}/status`, { status });
      return true;
    },
    { errorMessage: "Failed to update status", logContext: "feedback.setStatus" },
  );
  if (!ok) return;
  const item = items.value.find((i) => i.id === id);
  if (item) item.status = status;
  if (selectedItem.value?.id === id) {
    selectedItem.value = { ...selectedItem.value, status };
  }
  if (status !== filter.value) {
    removeFromList(id);
  }
}

async function advanceStatus(item: FeedbackItem): Promise<void> {
  const next = NEXT_STATUS[item.status];
  if (!next) return;
  await setStatus(item.id, next);
}

function openItem(item: FeedbackItem): void {
  selectedItem.value = item;
  drawerOpen.value = true;
  if (item.status === "unread") {
    void setStatus(item.id, "read");
  }
}

function closeDrawer(): void {
  drawerOpen.value = false;
  selectedItem.value = null;
}

function handleReply(): void {
  if (!selectedItem.value) return;
  reply(selectedItem.value);
}

async function archiveItem(item: FeedbackItem): Promise<void> {
  await setStatus(item.id, "archived");
  if (selectedItem.value?.id === item.id) closeDrawer();
}

async function unarchiveItem(item: FeedbackItem): Promise<void> {
  await setStatus(item.id, "read");
  if (selectedItem.value?.id === item.id) closeDrawer();
}

watch([filter, page, sort], () => {
  void load();
});

onMounted(load);
</script>

<template>
  <PageShell
    title="feedback"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'feedback' }]"
    back-to="/tools"
    max-width="5xl"
    body-width="column"
  >
    <AdminListSkeleton v-if="loading" label="Loading feedback" />

    <template v-else>
      <div class="page-tool-actions">
        <AdminListToolbar>
          <template #start>
            <AdminFilterDropdown
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
                  :active="filter === chip.value"
                  :color-class="feedbackStatusClass(chip.value)"
                  @click="setFilter(chip.value)"
                />
              </template>
            </AdminFilterDropdown>
          </template>
        </AdminListToolbar>
      </div>

      <EmptyState
        v-if="items.length === 0"
        class="mt-4"
        :description="`no feedback messages with status '${filter}'`"
      />

      <div v-else class="mt-1 w-full min-w-0 self-stretch">
        <AdminDataTable table-label="feedback messages">
          <template #header>
            <th :class="ADMIN_TH_CLASS">status</th>
            <th :class="ADMIN_TH_CLASS">who</th>
            <th :class="ADMIN_TH_CLASS" :aria-sort="sortAriaSort()">
              <button
                type="button"
                :class="ADMIN_SORT_HEADER_BUTTON_CLASS"
                aria-label="sort by when"
                @click="toggleCreatedSort"
              >
                <ChevronIcon class-name="size-3 shrink-0" />
                when{{ sortIndicator() }}
              </button>
            </th>
            <th :class="ADMIN_TH_CLASS">title</th>
            <th :class="[ADMIN_TH_CLASS, 'w-px text-right']" scope="col">actions</th>
          </template>

          <AdminDataRow
            v-for="item in items"
            :key="item.id"
            interactive
            nested-interactive
            :col-span="5"
            :expanded="drawerOpen && selectedItem?.id === item.id"
            @click="openItem(item)"
          >
            <td :class="ADMIN_TD_CLASS">
              <button
                type="button"
                class="inline-flex items-center gap-1.5 rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50"
                :aria-label="ADVANCE_STATUS_LABEL[item.status] ?? 'change status'"
                @click.stop="advanceStatus(item)"
                @keydown.stop
              >
                <RefreshIcon class-name="size-3.5 shrink-0" />
                <StatusBadge :label="item.status" :class-name="feedbackStatusClass(item.status)" />
              </button>
            </td>
            <td :class="ADMIN_TD_MUTED_CLASS" :title="item.email">{{ item.email }}</td>
            <td :class="ADMIN_TD_MUTED_CLASS">{{ formatDate(item.created_at) }}</td>
            <td :class="ADMIN_TD_TITLE_CLASS">
              <p class="truncate text-sm lowercase text-surface-light" :title="item.theme">
                {{ item.theme }}
              </p>
              <p class="mt-0.5 truncate text-xs text-surface-mid" :title="item.message">
                {{ item.message }}
              </p>
            </td>
            <template #actions>
              <IconActionButton
                v-if="item.status === 'archived'"
                quiet
                action="create"
                aria-label="unarchive"
                title="unarchive"
                @click="unarchiveItem(item)"
              >
                <ArchiveIcon restore class-name="size-4" />
              </IconActionButton>
              <IconActionButton
                v-else
                quiet
                action="create"
                aria-label="archive"
                title="archive"
                @click="archiveItem(item)"
              >
                <ArchiveIcon class-name="size-4" />
              </IconActionButton>
            </template>
          </AdminDataRow>
        </AdminDataTable>
      </div>

      <AdminListFooter
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="page < totalPages"
        :has-previous-page="page > 1"
        item-label="messages"
        aria-label="feedback pagination"
        @first="goToPage(1)"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
        @last="goToPage(totalPages)"
      />
    </template>

    <FeedbackDetailDrawer
      :open="drawerOpen"
      :item="selectedItem"
      @close="closeDrawer"
      @reply="handleReply"
    />
  </PageShell>
</template>
