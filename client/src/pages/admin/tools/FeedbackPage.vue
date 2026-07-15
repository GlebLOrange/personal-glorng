<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BasePagination from "@/components/ui/BasePagination.vue";
import { Card } from "@/components/ui/card";
import { LIST_PAGE_SIZE } from "@/constants/pagination";
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

const items = ref<FeedbackItem[]>([]);
const expandedId = ref<number | null>(null);
const filter = ref<"all" | "unread" | "archived">("all");
const page = ref(1);
const totalPages = ref(0);
const loading = ref(false);
const { toast } = useNotify();
const router = useRouter();

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
      per_page: LIST_PAGE_SIZE,
    };
    if (filter.value !== "all") {
      params.status = filter.value;
    }
    const { data } = await api.get<PaginatedList<FeedbackItem>>("/feedback", { params });
    items.value = data.items;
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
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    toast("Failed to update status", "error");
  }
}

function toggle(item: FeedbackItem): void {
  if (expandedId.value === item.id) {
    expandedId.value = null;
    return;
  }
  expandedId.value = item.id;
  if (item.status === "unread") setStatus(item.id, "read");
}

const statusColors: Record<string, string> = {
  unread: "bg-accent-blue/20 text-accent-blue",
  read: "bg-surface-border text-surface-mid",
  archived: "bg-surface-dark text-surface-muted",
};

watch([filter, page], () => {
  void load();
});

onMounted(load);
</script>

<template>
  <AdminPageLayout title="feedback">
    <header class="page-intro">
      <div class="flex flex-wrap gap-2">
        <BaseButton
          v-for="f in ['all', 'unread', 'archived'] as const"
          :key="f"
          :variant="filter === f ? 'primary' : 'ghost'"
          size="sm"
          @click="setFilter(f)"
        >
          {{ f.charAt(0).toUpperCase() + f.slice(1) }}
        </BaseButton>
      </div>
    </header>

    <div class="min-w-0 space-y-3" :aria-busy="loading || undefined">
      <Card
        v-for="item in items"
        :key="item.id"
        hoverable
        class="min-w-0 cursor-pointer"
        @click="toggle(item)"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="break-words text-sm font-bold text-surface-light">{{ item.theme }}</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded" :class="statusColors[item.status]">
                {{ item.status }}
              </span>
            </div>
            <div class="text-xs text-surface-mid">
              {{ item.email }} · {{ formatDate(item.created_at) }}
            </div>
          </div>
          <BaseButton
            v-if="item.status !== 'archived'"
            variant="ghost"
            size="sm"
            @click.stop="setStatus(item.id, 'archived')"
          >
            Archive
          </BaseButton>
        </div>

        <div v-if="expandedId === item.id" class="mt-3 pt-3 border-t border-surface-border">
          <p class="mb-3 whitespace-pre-wrap break-words text-sm text-surface-sage">{{ item.message }}</p>
          <BaseButton variant="ghost" size="sm" @click.stop="reply(item)"> Reply </BaseButton>
        </div>
      </Card>

      <p v-if="!loading && items.length === 0" class="text-surface-mid text-sm text-center py-8">
        No feedback messages{{ filter !== "all" ? ` with status "${filter}"` : "" }}.
      </p>

      <BasePagination
        v-if="totalPages > 1"
        aria-label="Feedback pagination"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="page < totalPages"
        :has-previous-page="page > 1"
        :loading="loading"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
      />
    </div>
  </AdminPageLayout>
</template>
