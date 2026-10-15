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
  ADMIN_MOBILE_LIST_CLASS,
  ADMIN_MOBILE_ROW_WRAP_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TD_TITLE_CLASS,
  ADMIN_TH_CLASS,
} from "@/constants/adminDataTable";
import FeedbackDetailDrawer from "@/components/admin/FeedbackDetailDrawer.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import ArchiveIcon from "@/components/icons/ArchiveIcon.vue";
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

const DEFAULT_STATUS_FILTER: StatusFilter = "unread";

const STATUS_FILTERS: { label: string; value: StatusFilter }[] = [
  { label: "unread", value: "unread" },
  { label: "read", value: "read" },
  { label: "archived", value: "archived" },
];

const items = ref<FeedbackItem[]>([]);
const selectedItem = ref<FeedbackItem | null>(null);
const drawerOpen = ref(false);
const filter = ref<StatusFilter>(DEFAULT_STATUS_FILTER);
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
  void router.push({ path: "/admin/send-email" });
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

function openItem(item: FeedbackItem): void {
  selectedItem.value = item;
  drawerOpen.value = true;
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

watch([filter, page], () => {
  void load();
});

onMounted(load);
</script>

<template>
  <AdminPageLayout title="feedback">
    <AdminListSkeleton v-if="loading" label="Loading feedback" />

    <template v-else>
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

      <EmptyState
        v-if="items.length === 0"
        class="mt-4"
        :description="`no feedback messages with status '${filter}'`"
      />

      <div v-else class="mt-1 min-w-0">
        <div :class="ADMIN_MOBILE_LIST_CLASS">
          <div
            v-for="item in items"
            :key="`m-${item.id}`"
            :class="[
              ADMIN_MOBILE_ROW_WRAP_CLASS,
              'flex min-w-0 cursor-pointer items-center gap-2',
              drawerOpen && selectedItem?.id === item.id ? 'bg-surface-card/50' : undefined,
            ]"
            role="button"
            tabindex="0"
            @click="openItem(item)"
            @keydown.enter.prevent="openItem(item)"
            @keydown.space.prevent="openItem(item)"
          >
            <StatusBadge :label="item.status" :class-name="feedbackStatusClass(item.status)" />
            <span class="shrink-0 text-xs lowercase text-surface-muted" :title="item.email">
              {{ item.email }}
            </span>
            <span class="shrink-0 text-xs lowercase text-surface-muted">
              {{ formatDate(item.created_at) }}
            </span>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm lowercase text-surface-light" :title="item.theme">
                {{ item.theme }}
              </p>
              <p class="mt-0.5 truncate text-xs text-surface-mid" :title="item.message">
                {{ item.message }}
              </p>
            </div>
            <div class="flex shrink-0 items-center" @click.stop @keydown.stop>
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
            </div>
          </div>
        </div>

        <AdminDataTable table-label="feedback messages">
          <template #header>
            <th :class="ADMIN_TH_CLASS">status</th>
            <th :class="ADMIN_TH_CLASS">who</th>
            <th :class="ADMIN_TH_CLASS">when</th>
            <th :class="ADMIN_TH_CLASS">title</th>
            <th class="w-px px-2 text-right">
              <span class="sr-only">actions</span>
            </th>
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
              <StatusBadge :label="item.status" :class-name="feedbackStatusClass(item.status)" />
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
  </AdminPageLayout>
</template>
