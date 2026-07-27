<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef, watch } from "vue";
import { useRouter } from "vue-router";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import FeedbackDetailDrawer from "@/components/admin/FeedbackDetailDrawer.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
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

const STATUS_FILTERS: { label: string; value: StatusFilter }[] = [
  { label: "unread", value: "unread" },
  { label: "read", value: "read" },
  { label: "archived", value: "archived" },
];

const items = ref<FeedbackItem[]>([]);
const selectedItem = ref<FeedbackItem | null>(null);
const drawerOpen = ref(false);
/** null = show all statuses (default). */
const filter = ref<StatusFilter | null>(null);
const page = ref(1);
const total = ref(0);
const totalPages = ref(0);
const { loading, run: runLoad } = useApiAction();
const { run: runStatus } = useApiAction();
const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");
const router = useRouter();

const hasActiveFilters = computed(() => filter.value !== null);
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
          ...(filter.value ? { status: filter.value } : {}),
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
  filter.value = null;
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
  if (filter.value !== null && status !== filter.value) {
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
        :description="
          filter ? `no feedback messages with status '${filter}'` : 'no feedback messages'
        "
      />

      <div v-else class="mt-1 min-w-0 space-y-2">
        <AdminListRow
          v-for="item in items"
          :key="item.id"
          interactive
          nested-interactive
          reveal-actions-on-hover
          :status-class="feedbackStatusClass(item.status)"
          :expanded="drawerOpen && selectedItem?.id === item.id"
          @click="openItem(item)"
        >
          <template #badge>
            <div class="flex items-center gap-2">
              <StatusBadge :label="item.status" :class-name="feedbackStatusClass(item.status)" />
              <span class="whitespace-nowrap text-xs lowercase text-surface-muted">
                {{ formatDate(item.created_at) }}
              </span>
              <span class="hidden max-w-[12rem] truncate text-xs lowercase text-surface-muted sm:inline">
                {{ item.email }}
              </span>
            </div>
          </template>
          <template #primary>
            <span class="lowercase" :title="item.theme">{{ item.theme }}</span>
          </template>
          <template #actions>
            <IconEditButton aria-label="edit feedback" @click="openItem(item)" />
            <BaseButton
              v-if="item.status === 'archived'"
              variant="ghost"
              quiet
              size="sm"
              @click="unarchiveItem(item)"
            >
              unarchive
            </BaseButton>
            <BaseButton v-else variant="ghost" quiet size="sm" @click="archiveItem(item)">
              archive
            </BaseButton>
          </template>
        </AdminListRow>
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
