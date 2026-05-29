<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
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
const { toast } = useNotify();
const router = useRouter();

function reply(item: FeedbackItem): void {
  const body = `\n\n--- Original ---\n${item.message}`;
  router.push({
    path: "/admin/tools/email",
    query: { to: item.email, subject: `Re: ${item.theme}`, body },
  });
}

const filtered = computed(() => {
  if (filter.value === "all") return items.value;
  return items.value.filter((i) => i.status === filter.value);
});

async function load(): Promise<void> {
  try {
    const { data } = await api.get<FeedbackItem[]>("/feedback");
    items.value = data;
  } catch (err) {
    console.error(err);
    toast("Failed to load feedback", "error");
  }
}

async function setStatus(id: number, status: string): Promise<void> {
  try {
    await api.patch(`/feedback/${id}/status`, { status });
    const item = items.value.find((i) => i.id === id);
    if (item) item.status = status;
  } catch (err) {
    console.error(err);
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

onMounted(load);
</script>

<template>
  <AdminPageLayout title="feedback">
    <div class="flex gap-2 mb-6">
      <BaseButton
        v-for="f in ['all', 'unread', 'archived'] as const"
        :key="f"
        :variant="filter === f ? 'primary' : 'ghost'"
        size="sm"
        @click="filter = f"
      >
        {{ f.charAt(0).toUpperCase() + f.slice(1) }}
      </BaseButton>
    </div>

    <div class="space-y-3">
      <BaseCard
        v-for="item in filtered"
        :key="item.id"
        hoverable
        class="cursor-pointer"
        @click="toggle(item)"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-surface-light font-bold text-sm truncate">{{ item.theme }}</span>
              <span
                class="text-[10px] font-mono px-1.5 py-0.5 rounded"
                :class="statusColors[item.status]"
              >
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
          <p class="text-sm text-surface-sage whitespace-pre-wrap mb-3">{{ item.message }}</p>
          <BaseButton variant="ghost" size="sm" @click.stop="reply(item)"> Reply </BaseButton>
        </div>
      </BaseCard>

      <p v-if="filtered.length === 0" class="text-surface-mid text-sm text-center py-8">
        No feedback messages{{ filter !== "all" ? ` with status "${filter}"` : "" }}.
      </p>
    </div>
  </AdminPageLayout>
</template>
