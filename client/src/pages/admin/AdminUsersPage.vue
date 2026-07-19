<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef, watch } from "vue";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import AdminListToolbar from "@/components/admin/AdminListToolbar.vue";
import AdminUserPermissionsEditor from "@/components/admin/AdminUserPermissionsEditor.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { Card } from "@/components/ui/card";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import {
  userRoleClass,
  userStatusClass,
} from "@/constants/filterColors";
import { LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { usePlatformCatalog } from "@/composables/usePlatformCatalog";
import type { AdminUserSummary, PaginatedList } from "@/types";
import { getApiErrorMessage } from "@/types/api";
import { formatDate } from "@/utils/format";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";

type RoleFilter = "all" | "superuser" | "custom";
type StatusFilter = "all" | "verified" | "unverified" | "protected";
type BadgeView = { id: string; label: string; className: string };

interface AdminUsersStats {
  total: number;
  superuser_count: number;
  protected_count: number;
  unverified_count: number;
}

const ROLE_FILTERS: { label: string; value: Exclude<RoleFilter, "all"> }[] = [
  { label: "superusers", value: "superuser" },
  { label: "custom access", value: "custom" },
];

const STATUS_FILTERS: { label: string; value: Exclude<StatusFilter, "all"> }[] = [
  { label: "verified", value: "verified" },
  { label: "unverified", value: "unverified" },
  { label: "protected", value: "protected" },
];

const { toast } = useNotify();
const users = ref<AdminUserSummary[]>([]);
const userStats = ref<AdminUsersStats | null>(null);
const page = ref(1);
const total = ref(0);
const totalPages = ref(0);
const { services, load: loadPlatformCatalog } = usePlatformCatalog();
const loading = ref(false);
const savingId = ref<string | null>(null);
const draftPermissions = ref<Record<string, string[]>>({});
const searchQuery = ref("");
const debouncedSearch = ref("");
const roleFilter = ref<RoleFilter>("all");
const statusFilter = ref<StatusFilter>("all");
const filterDropdownRef = useTemplateRef<{ close: () => void }>("filterDropdown");
const selectedUserId = ref<string | null>(null);

const superuserCount = computed(() => userStats.value?.superuser_count ?? 0);
const hasNextPage = computed(() => page.value < totalPages.value);
const hasPreviousPage = computed(() => page.value > 1);
const hasActiveFilters = computed(
  () => roleFilter.value !== "all" || statusFilter.value !== "all",
);
const activeFilterLabel = computed(() => {
  const parts: string[] = [];
  const role = ROLE_FILTERS.find((chip) => chip.value === roleFilter.value)?.label;
  const status = STATUS_FILTERS.find((chip) => chip.value === statusFilter.value)?.label;
  if (role) parts.push(role);
  if (status) parts.push(status);
  return parts.length ? parts.join(", ") : undefined;
});

const selectedUser = computed(
  () => users.value.find((user) => user.id === selectedUserId.value) ?? null,
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

function permissionCount(user: AdminUserSummary): number {
  return (draftPermissions.value[user.id] ?? user.permissions).filter(
    (permission) => permission !== SUPERUSER_PERMISSION,
  ).length;
}

function roleBadge(user: AdminUserSummary): BadgeView {
  const isSuperuser = user.permissions.includes(SUPERUSER_PERMISSION);
  return {
    id: "role",
    label: isSuperuser ? "superuser" : "custom access",
    className: isSuperuser ? userRoleClass("superuser") : userRoleClass("custom"),
  };
}

function statusBadges(user: AdminUserSummary): BadgeView[] {
  return [
    ...(user.is_protected
      ? [{ id: "protected", label: "protected", className: userStatusClass("protected") }]
      : []),
    user.is_verified
      ? { id: "verified", label: "verified", className: userStatusClass("verified") }
      : { id: "unverified", label: "unverified", className: userStatusClass("unverified") },
  ];
}

function setRoleFilter(next: Exclude<RoleFilter, "all">): void {
  roleFilter.value = next;
  page.value = 1;
  filterDropdownRef.value?.close();
}

function setUserStatusFilter(next: Exclude<StatusFilter, "all">): void {
  statusFilter.value = next;
  page.value = 1;
  filterDropdownRef.value?.close();
}

function clearFilters(): void {
  roleFilter.value = "all";
  statusFilter.value = "all";
  page.value = 1;
  filterDropdownRef.value?.close();
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
  try {
    const { data } = await api.get<AdminUsersStats>("/admin/users/stats");
    userStats.value = data;
  } catch (err) {
    toast(getApiErrorMessage(err, "Failed to load user stats"), "error");
  }
}

async function loadUsers(): Promise<void> {
  loading.value = true;
  try {
    const params: Record<string, string | number> = {
      page: page.value,
      per_page: LIST_PAGE_SIZE,
      role: roleFilter.value,
      status: statusFilter.value,
    };
    const query = debouncedSearch.value.trim();
    if (query) params.search = query;

    const { data } = await api.get<PaginatedList<AdminUserSummary>>("/admin/users", { params });
    users.value = data.items;
    total.value = data.total;
    totalPages.value = data.pages;
    for (const user of data.items) {
      draftPermissions.value[user.id] = draftPermissions.value[user.id] ?? [...user.permissions];
    }
  } catch (err) {
    toast(getApiErrorMessage(err, "Failed to load users"), "error");
  } finally {
    loading.value = false;
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
    debouncedSearch.value = value;
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
  try {
    const permissions = draftPermissions.value[user.id] ?? [];
    const { data } = await api.patch<AdminUserSummary>(`/admin/users/${user.id}/permissions`, {
      permissions,
    });
    const index = users.value.findIndex((row) => row.id === user.id);
    if (index >= 0) {
      users.value[index] = data;
      draftPermissions.value[user.id] = [...data.permissions];
    }
    toast("Permissions updated", "success");
    await loadUserStats();
  } catch (err) {
    draftPermissions.value[user.id] = [...user.permissions];
    toast(getApiErrorMessage(err, "Failed to update permissions"), "error");
  } finally {
    savingId.value = null;
  }
}

onMounted(() => {
  void Promise.all([loadUsers(), loadUserStats(), loadPlatformCatalog()]);
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
      <AdminListToolbar>
        <template #start>
          <div class="flex w-full min-w-0 flex-col gap-3">
            <BaseInput
              v-model="searchQuery"
              type="search"
              placeholder="search users by name or email"
              aria-label="search users by name or email"
              class="w-full"
            />
            <AdminFilterDropdown
              ref="filterDropdown"
              :has-active-filters="hasActiveFilters"
              :active-label="activeFilterLabel"
              @clear="clearFilters"
            >
              <div>
                <p class="text-xs font-medium text-surface-mid mb-2">role</p>
                <div class="grid grid-cols-3 gap-2">
                  <AdminFilterChip
                    v-for="chip in ROLE_FILTERS"
                    :key="chip.value"
                    :label="chip.label"
                    :active="roleFilter === chip.value"
                    :color-class="userRoleClass(chip.value)"
                    @click="setRoleFilter(chip.value)"
                  />
                </div>
              </div>

              <div>
                <p class="text-xs font-medium text-surface-mid mb-2">status</p>
                <div class="grid grid-cols-3 gap-2">
                  <AdminFilterChip
                    v-for="chip in STATUS_FILTERS"
                    :key="chip.value"
                    :label="chip.label"
                    :active="statusFilter === chip.value"
                    :color-class="userStatusClass(chip.value)"
                    @click="setUserStatusFilter(chip.value)"
                  />
                </div>
              </div>
            </AdminFilterDropdown>
          </div>
        </template>
      </AdminListToolbar>

      <EmptyState v-if="users.length === 0">
        No users match the current filters.
      </EmptyState>

      <div v-else class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <button
          v-for="user in users"
          :key="user.id"
          type="button"
          class="interactive-surface h-full w-full p-4 text-left transition-colors"
          :aria-label="`Open permissions for ${user.display_name || user.email}`"
          @click="openUserDrawer(user)"
        >
          <span class="flex min-h-full flex-col gap-4">
            <span class="flex items-start justify-between gap-3">
              <span class="min-w-0">
                <span class="block truncate text-base font-semibold text-surface-light">
                  {{ user.display_name || user.email }}
                </span>
                <span class="mt-1 block truncate text-xs text-surface-mid">{{ user.email }}</span>
              </span>
              <StatusBadge :label="roleBadge(user).label" :class-name="roleBadge(user).className" />
            </span>

            <span class="flex flex-wrap gap-2">
              <StatusBadge
                v-for="badge in statusBadges(user)"
                :key="badge.id"
                :label="badge.label"
                :class-name="badge.className"
              />
            </span>

            <span
              class="mt-auto flex items-center justify-between gap-3 text-xs text-surface-muted"
            >
              <span>{{ permissionCount(user) }} permissions</span>
              <span>Joined {{ formatDate(user.created_at) }}</span>
            </span>
          </span>
        </button>
      </div>

      <AdminListFooter
        :total="total"
        :page="page"
        :total-pages="totalPages"
        :has-next-page="hasNextPage"
        :has-previous-page="hasPreviousPage"
        :loading="loading"
        :visible-count="users.length"
        item-label="users"
        aria-label="Users pagination"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
      />
    </template>

    <BaseDrawer
      :open="selectedUser !== null"
      :title="selectedUser ? selectedUser.display_name || selectedUser.email : 'User permissions'"
      max-width="xl"
      @close="requestCloseUserDrawer"
    >
      <template v-if="selectedUser">
        <p class="mb-1 text-xs font-medium uppercase tracking-wide text-surface-muted">
          User permissions
        </p>
        <p class="mb-5 break-all text-xs text-surface-mid">{{ selectedUser.email }}</p>

        <div class="mb-5 space-y-3">
          <div class="flex flex-wrap gap-2">
            <StatusBadge
              :label="roleBadge(selectedUser).label"
              :class-name="roleBadge(selectedUser).className"
            />
            <StatusBadge
              v-for="badge in statusBadges(selectedUser)"
              :key="badge.id"
              :label="badge.label"
              :class-name="badge.className"
            />
          </div>
          <p class="text-xs text-surface-muted">
            Joined {{ formatDate(selectedUser.created_at) }} ·
            {{ permissionCount(selectedUser) }} tool permissions selected
          </p>
          <p
            v-if="selectedUser.is_protected"
            class="rounded-lg border border-accent-blue/30 bg-accent-blue/10 px-3 py-2 text-xs text-accent-blue"
          >
            Protected accounts are managed by the system and cannot be edited here.
          </p>
        </div>

        <AdminUserPermissionsEditor
          :permissions="draftPermissions[selectedUser.id] ?? []"
          :disabled="selectedUser.is_protected"
          :lock-superuser="isLastSuperuser(selectedUser)"
          :services="services"
          @update:permissions="setDraftPermissions(selectedUser.id, $event)"
        />
      </template>

      <template v-if="selectedUser" #footer>
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p class="text-xs text-surface-muted">
            {{
              hasDraftChanges(selectedUser)
                ? "Unsaved permission changes"
                : "Permissions are up to date"
            }}
          </p>
          <div class="flex gap-2">
            <BaseButton variant="ghost" @click="requestCloseUserDrawer">cancel</BaseButton>
            <BaseButton
              variant="primary"
              :loading="savingId === selectedUser.id"
              :disabled="selectedUser.is_protected || !hasDraftChanges(selectedUser)"
              @click="savePermissions(selectedUser)"
            >
              {{ savingId === selectedUser.id ? "Saving..." : "Save permissions" }}
            </BaseButton>
          </div>
        </div>
      </template>
    </BaseDrawer>
  </AdminPageLayout>
</template>
