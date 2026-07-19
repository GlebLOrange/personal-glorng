<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef, watch } from "vue";
import { useRouter } from "vue-router";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import FeedbackDetailDrawer from "@/components/admin/FeedbackDetailDrawer.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { feedbackStatusClass } from "@/constants/filterColors";
import { ADMIN_LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import type { PaginatedList } from "@/types";
import { formatDate } from "@/utils/format";

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
const filter = ref<StatusFilter>("unread");
const page = ref(1);
const total = ref(0);
const totalPages = ref(0);
const loading = ref(false);
const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");
const { toast } = useNotify();
const router = useRouter();

const hasActiveFilters = computed(() => filter.value !== "unread");
const activeFilterLabel = computed(
  () => STATUS_FILTERS.find((chip) => chip.value === filter.value)?.label,
);

function reply(item: FeedbackItem): void {
  const body = `\n\n--- Original ---\n${item.message}`;
  router.push({
    path: "/admin/tools/email",
    query: { to: item.email, subject: `Re: ${item.theme}`, body },
  });
}

function removeFromList(id: number): void {
  const idx = items.value.findIndex((item) => item.id === id);
  if (idx === -1) return;
  items.value.splice(idx, 1);
  total.value = Math.max(0, total.value - 1);
}

async function load(): Promise<void> {
  loading.value = true;
  try {
    const { data } = await api.get<PaginatedList<FeedbackItem>>("/feedback", {
      params: {
        page: page.value,
        per_page: ADMIN_LIST_PAGE_SIZE,
        status: filter.value,
      },
    });
    items.value = data.items;
    total.value = data.total;
    totalPages.value = data.pages;
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to load feedback", "error");
  } finally {
    loading.value = false;
  }
}

function setFilter(next: StatusFilter): void {
  filter.value = next;
  page.value = 1;
  filterDropdownRef.value?.close();
}

function clearFilters(): void {
  filter.value = "unread";
  page.value = 1;
  filterDropdownRef.value?.close();
}

function goToPage(nextPage: number): void {
  if (nextPage < 1) return;
  if (totalPages.value > 0 && nextPage > totalPages.value) return;
  page.value = nextPage;
}

async function setStatus(id: number, status: string): Promise<void> {
  try {
    await api.patch(`/feedback/${id}/status`, { status });
    const item = items.value.find((i) => i.id === id);
    if (item) item.status = status;
    if (selectedItem.value?.id === id) {
      selectedItem.value = { ...selectedItem.value, status };
    }
    if (status !== filter.value) {
      removeFromList(id);
    }
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to update status", "error");
  }
}

function openItem(item: FeedbackItem): void {
  selectedItem.value = item;
  drawerOpen.value = true;
  // ponytail: opening = read; archive in the same step (no separate read linger)
  if (item.status !== "archived") void setStatus(item.id, "archived");
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
  <AdminPageLayout hub="tools" title="feedback">
    <AdminListSkeleton v-if="loading" label="Loading feedback" />

    <template v-else>
      <AdminListToolbar>
        <template #start>
          <AdminFilterDropdown
            ref="filterDropdown"
            :has-active-filters="hasActiveFilters"
            :active-label="activeFilterLabel"
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
        :description="`No feedback messages with status '${filter}'.`"
      />

      <div v-else class="min-w-0 mt-1 space-y-1">
        <AdminListRow
          v-for="item in items"
          :key="item.id"
          interactive
          nested-interactive
          @click="openItem(item)"
        >
          <template #badge>
            <StatusBadge :label="item.status" :class-name="feedbackStatusClass(item.status)" />
          </template>
          <template #primary>
            <span :title="item.theme">{{ item.theme }}</span>
          </template>
          <template #meta>
            <span>{{ item.email }}</span>
          </template>
          <template #time>{{ formatDate(item.created_at) }}</template>
          <template #actions>
            <BaseButton
              v-if="item.status === 'archived'"
              variant="ghost"
              quiet
              size="sm"
              @click="unarchiveItem(item)"
            >
              unarchive
            </BaseButton>
            <BaseButton
              v-else
              variant="ghost"
              quiet
              size="sm"
              @click="archiveItem(item)"
            >
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
        ariaLabel="Feedback pagination"
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
