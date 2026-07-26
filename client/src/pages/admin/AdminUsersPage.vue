<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminUsersGrid from "@/components/admin/users/AdminUsersGrid.vue";
import AdminUsersPermissionsDrawer from "@/components/admin/users/AdminUsersPermissionsDrawer.vue";
import AdminUsersToolbar from "@/components/admin/users/AdminUsersToolbar.vue";
import type {
  RoleFilter,
  StatusFilter,
} from "@/components/admin/users/AdminUsersToolbar.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import { Card } from "@/components/ui/card";
import EmptyState from "@/components/ui/EmptyState.vue";
import { LIST_PAGE_SIZE } from "@/constants/pagination";
import { effectiveSearchQuery } from "@/constants/search";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { usePlatformCatalog } from "@/composables/usePlatformCatalog";
import type { AdminUserSummary, PaginatedList } from "@/types";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";

interface AdminUsersStats {
  total: number;
  superuser_count: number;
  protected_count: number;
  unverified_count: number;
}

const users = ref<AdminUserSummary[]>([]);
const userStats = ref<AdminUsersStats | null>(null);
const page = ref(1);
const total = ref(0);
const totalPages = ref(0);
const { services, load: loadPlatformCatalog } = usePlatformCatalog();
const { loading, run: runLoadUsers } = useApiAction();
const { run: runLoadStats } = useApiAction();
const { run: runSavePermissions } = useApiAction();
const savingId = ref<string | null>(null);
const draftPermissions = ref<Record<string, string[]>>({});
const searchQuery = ref("");
const debouncedSearch = ref("");
const roleFilter = ref<RoleFilter>("all");
const statusFilter = ref<StatusFilter>("all");
const selectedUserId = ref<string | null>(null);

const superuserCount = computed(() => userStats.value?.superuser_count ?? 0);
const hasNextPage = computed(() => page.value < totalPages.value);
const hasPreviousPage = computed(() => page.value > 1);

const selectedUser = computed(
  () => users.value.find((user) => user.id === selectedUserId.value) ?? null,
);

const selectedDraftPermissions = computed(() =>
  selectedUser.value
    ? (draftPermissions.value[selectedUser.value.id] ?? selectedUser.value.permissions)
    : [],
);

useScrollListFingerprint(
  () =>
    `${debouncedSearch.value}:${roleFilter.value}:${statusFilter.value}:${page.value}:${users.value[0]?.id ?? ""}`,
);

function isLastSuperuser(user: AdminUserSummary): boolean {
  return user.permissions.includes(SUPERUSER_PERMISSION) && superuserCount.value <= 1;
}

function hasDraftChanges(user: AdminUserSummary): boolean {
  const draft = draftPermissions.value[user.id] ?? [];
  if (draft.length !== user.permissions.length) return true;
  const current = new Set(user.permissions);
  return draft.some((permission) => !current.has(permission));
}

function setDraftPermissions(userId: string, permissions: string[]): void {
  draftPermissions.value[userId] = permissions;
}

function openUserDrawer(user: AdminUserSummary): void {
  selectedUserId.value = user.id;
  draftPermissions.value[user.id] = draftPermissions.value[user.id] ?? [...user.permissions];
}

function closeUserDrawer(): void {
  const user = selectedUser.value;
  if (user) draftPermissions.value[user.id] = [...user.permissions];
  selectedUserId.value = null;
}

function requestCloseUserDrawer(): void {
  const user = selectedUser.value;
  if (user && hasDraftChanges(user) && !window.confirm("Discard unsaved permission changes?")) {
    return;
  }
  closeUserDrawer();
}

async function loadUserStats(): Promise<void> {
  const data = await runLoadStats(
    async () => {
      const response = await api.get<AdminUsersStats>("/admin/users/stats");
      return response.data;
    },
    { errorMessage: "Failed to load user stats", logContext: "admin.users.stats" },
  );
  if (data) userStats.value = data;
}

async function loadUsers(): Promise<void> {
  const data = await runLoadUsers(
    async () => {
      const params: Record<string, string | number> = {
        page: page.value,
        per_page: LIST_PAGE_SIZE,
        role: roleFilter.value,
        status: statusFilter.value,
      };
      const query = effectiveSearchQuery(debouncedSearch.value);
      if (query) params.search = query;

      const response = await api.get<PaginatedList<AdminUserSummary>>("/admin/users", { params });
      return response.data;
    },
    { errorMessage: "Failed to load users", logContext: "admin.users.list" },
  );
  if (!data) return;
  users.value = data.items;
  total.value = data.total;
  totalPages.value = data.pages;
  for (const user of data.items) {
    draftPermissions.value[user.id] = draftPermissions.value[user.id] ?? [...user.permissions];
  }
}

function goToPage(nextPage: number): void {
  if (nextPage < 1) return;
  if (totalPages.value > 0 && nextPage > totalPages.value) return;
  page.value = nextPage;
}

let searchDebounceTimer: ReturnType<typeof setTimeout> | undefined;
watch(searchQuery, (value) => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    const next = effectiveSearchQuery(value) ?? "";
    if (next === debouncedSearch.value) return;
    debouncedSearch.value = next;
    page.value = 1;
  }, 300);
});

watch([debouncedSearch, roleFilter, statusFilter], () => {
  page.value = 1;
});

watch([page, debouncedSearch, roleFilter, statusFilter], () => {
  void loadUsers();
});

async function savePermissions(user: AdminUserSummary): Promise<void> {
  savingId.value = user.id;
  const data = await runSavePermissions(
    async () => {
      const permissions = draftPermissions.value[user.id] ?? [];
      const response = await api.patch<AdminUserSummary>(`/admin/users/${user.id}/permissions`, {
        permissions,
      });
      return response.data;
    },
    {
      successMessage: "Permissions updated",
      errorMessage: "Failed to update permissions",
      logContext: "admin.users.permissions",
    },
  );
  if (!data) {
    draftPermissions.value[user.id] = [...user.permissions];
    savingId.value = null;
    return;
  }
  const index = users.value.findIndex((row) => row.id === user.id);
  if (index >= 0) {
    users.value[index] = data;
    draftPermissions.value[user.id] = [...data.permissions];
  }
  savingId.value = null;
  await loadUserStats();
}

onMounted(() => {
  void Promise.all([loadUsers(), loadUserStats(), loadPlatformCatalog()]);
});

onUnmounted(() => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
});
</script>

<template>
  <AdminPageLayout title="users" max-width="xl">
    <div v-if="loading" class="space-y-4" aria-busy="true" aria-label="Loading users">
      <Card v-for="index in 3" :key="index">
        <div class="animate-pulse space-y-4">
          <div class="flex items-center justify-between gap-4">
            <div class="space-y-2">
              <div class="h-4 w-48 rounded bg-surface-border" />
              <div class="h-3 w-64 rounded bg-surface-border/70" />
            </div>
            <div class="h-7 w-28 rounded bg-surface-border/70" />
          </div>
          <div class="h-24 rounded bg-surface-dark" />
        </div>
      </Card>
    </div>

    <template v-else>
      <AdminUsersToolbar
        v-model:search-query="searchQuery"
        v-model:role-filter="roleFilter"
        v-model:status-filter="statusFilter"
      />

      <EmptyState v-if="users.length === 0"> No users match the current filters. </EmptyState>

      <AdminUsersGrid
        v-else
        :users="users"
        :draft-permissions="draftPermissions"
        @select="openUserDrawer"
      />

      <AdminListFooter
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="hasNextPage"
        :has-previous-page="hasPreviousPage"
        :loading="loading"
        :visible-count="users.length"
        item-label="users"
        ariaLabel="Users pagination"
        @first="goToPage(1)"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
        @last="goToPage(totalPages)"
      />
    </template>

    <AdminUsersPermissionsDrawer
      :user="selectedUser"
      :draft-permissions="selectedDraftPermissions"
      :services="services"
      :saving="selectedUser !== null && savingId === selectedUser.id"
      :lock-superuser="selectedUser !== null && isLastSuperuser(selectedUser)"
      :has-draft-changes="selectedUser !== null && hasDraftChanges(selectedUser)"
      @close="requestCloseUserDrawer"
      @save="selectedUser && savePermissions(selectedUser)"
      @update:permissions="selectedUser && setDraftPermissions(selectedUser.id, $event)"
    />
  </AdminPageLayout>
</template>
