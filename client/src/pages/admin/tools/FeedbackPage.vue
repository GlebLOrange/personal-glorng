<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminListRow from "@/components/admin/AdminListRow.vue";
import AdminListSkeleton from "@/components/admin/AdminListSkeleton.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import FeedbackDetailDrawer from "@/components/admin/FeedbackDetailDrawer.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
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

const FILTER_OPTIONS = ["all", "unread", "archived"] as const;

const items = ref<FeedbackItem[]>([]);
const selectedItem = ref<FeedbackItem | null>(null);
const drawerOpen = ref(false);
const filter = ref<"all" | "unread" | "archived">("all");
const page = ref(1);
const total = ref(0);
const totalPages = ref(0);
const loading = ref(false);
const { toast } = useNotify();
const router = useRouter();

const statusColors: Record<string, string> = {
  unread: "bg-accent-blue/20 text-accent-blue border-accent-blue/30",
  read: "bg-surface-border text-surface-mid border-surface-border",
  archived: "bg-surface-dark text-surface-muted border-surface-border",
};

function reply(item: FeedbackItem): void {
  const body = `\n\n--- Original ---\n${item.message}`;
  router.push({
    path: "/admin/tools/email",
    query: { to: item.email, subject: `Re: ${item.theme}`, body },
  });
}

async function load(): Promise<void> {
  loading.value = true;
  try {
    const params: Record<string, string | number> = {
      page: page.value,
      per_page: ADMIN_LIST_PAGE_SIZE,
    };
    if (filter.value !== "all") {
      params.status = filter.value;
    }
    const { data } = await api.get<PaginatedList<FeedbackItem>>("/feedback", { params });
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

function setFilter(next: "all" | "unread" | "archived"): void {
  filter.value = next;
  page.value = 1;
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
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to update status", "error");
  }
}

function openItem(item: FeedbackItem): void {
  selectedItem.value = item;
  drawerOpen.value = true;
  if (item.status === "unread") void setStatus(item.id, "read");
}

function closeDrawer(): void {
  drawerOpen.value = false;
  selectedItem.value = null;
}

function handleReply(): void {
  if (!selectedItem.value) return;
  reply(selectedItem.value);
}

async function handleArchive(): Promise<void> {
  if (!selectedItem.value) return;
  await setStatus(selectedItem.value.id, "archived");
  closeDrawer();
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
      <AdminListToolbar
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="page < totalPages"
        :has-previous-page="page > 1"
        item-label="messages"
        ariaLabel="Feedback pagination"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
      >
        <template #start>
          <div class="flex flex-wrap gap-2">
            <AdminFilterChip
              v-for="f in FILTER_OPTIONS"
              :key="f"
              :label="f"
              :active="filter === f"
              color-class="text-surface-light bg-surface-dark"
              @click="setFilter(f)"
            />
          </div>
        </template>
      </AdminListToolbar>

      <EmptyState
        v-if="items.length === 0"
        class="mt-4"
        :description="
          filter !== 'all' ? `No feedback messages with status '${filter}'.` : 'No feedback messages.'
        "
      />

      <div v-else class="min-w-0 mt-1 space-y-1">
        <AdminListRow
          v-for="item in items"
          :key="item.id"
          interactive
          @click="openItem(item)"
        >
          <template #badge>
            <StatusBadge :label="item.status" :class-name="statusColors[item.status]" />
          </template>
          <template #primary>
            <span :title="item.theme">{{ item.theme }}</span>
          </template>
          <template #meta>
            <span>{{ item.email }}</span>
          </template>
          <template #time>{{ formatDate(item.created_at) }}</template>
        </AdminListRow>
      </div>
    </template>

    <FeedbackDetailDrawer
      :open="drawerOpen"
      :item="selectedItem"
      @close="closeDrawer"
      @reply="handleReply"
      @archive="handleArchive"
    />
  </AdminPageLayout>
</template>
