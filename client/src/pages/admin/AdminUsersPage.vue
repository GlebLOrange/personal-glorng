<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";

import AdminUserPermissionsEditor from "@/components/admin/AdminUserPermissionsEditor.vue";
import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import { FIELD_INPUT_CLASS, SELECT_CLASS_COMPACT } from "@/constants/formClasses";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";
import { usePlatformCatalog } from "@/composables/usePlatformCatalog";
import type { AdminUserSummary } from "@/types";
import { getApiErrorMessage } from "@/types/api";
import { formatDate } from "@/utils/format";
import { SUPERUSER_PERMISSION } from "@/utils/permissions";

type RoleFilter = "all" | "superuser" | "custom";
type StatusFilter = "all" | "verified" | "unverified" | "protected";

const { toast } = useNotify();
const users = ref<AdminUserSummary[]>([]);
const { services, load: loadPlatformCatalog } = usePlatformCatalog();
const loading = ref(false);
const savingId = ref<string | null>(null);
const draftPermissions = ref<Record<string, string[]>>({});
const searchQuery = ref("");
const roleFilter = ref<RoleFilter>("all");
const statusFilter = ref<StatusFilter>("all");
const selectedUserId = ref<string | null>(null);

const superuserCount = computed(
  () => users.value.filter((u) => u.permissions.includes(SUPERUSER_PERMISSION)).length,
);
const protectedCount = computed(() => users.value.filter((u) => u.is_protected).length);
const unverifiedCount = computed(() => users.value.filter((u) => !u.is_verified).length);

const filteredUsers = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();

  return users.value.filter((user) => {
    const matchesSearch =
      !query ||
      user.email.toLowerCase().includes(query) ||
      (user.display_name ?? "").toLowerCase().includes(query);
    const isSuperuser = user.permissions.includes(SUPERUSER_PERMISSION);
    const matchesRole =
      roleFilter.value === "all" ||
      (roleFilter.value === "superuser" && isSuperuser) ||
      (roleFilter.value === "custom" && !isSuperuser);
    const matchesStatus =
      statusFilter.value === "all" ||
      (statusFilter.value === "verified" && user.is_verified) ||
      (statusFilter.value === "unverified" && !user.is_verified) ||
      (statusFilter.value === "protected" && user.is_protected);

    return matchesSearch && matchesRole && matchesStatus;
  });
});
const selectedUser = computed(
  () => users.value.find((user) => user.id === selectedUserId.value) ?? null,
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

function roleLabel(user: AdminUserSummary): string {
  return user.permissions.includes(SUPERUSER_PERMISSION) ? "superuser" : "custom access";
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

function onKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape" && selectedUser.value) closeUserDrawer();
}

async function loadUsers(): Promise<void> {
  loading.value = true;
  try {
    const { data } = await api.get<AdminUserSummary[]>("/admin/users");
    users.value = data;
    for (const user of data) {
      draftPermissions.value[user.id] = [...user.permissions];
    }
  } catch (err) {
    toast(getApiErrorMessage(err, "Failed to load users"), "error");
  } finally {
    loading.value = false;
  }
}

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
  } catch (err) {
    draftPermissions.value[user.id] = [...user.permissions];
    toast(getApiErrorMessage(err, "Failed to update permissions"), "error");
  } finally {
    savingId.value = null;
  }
}

onMounted(() => {
  document.addEventListener("keydown", onKeydown);
  void Promise.all([loadUsers(), loadPlatformCatalog()]);
});

onUnmounted(() => document.removeEventListener("keydown", onKeydown));
</script>

<template>
  <AdminPageLayout title="users" max-width="xl">
    <div class="mb-6 space-y-4">
      <p class="text-sm text-surface-mid">
        Manage tool permissions and promote users to platform superuser. Users cannot change these
        themselves.
      </p>

      <BaseCard>
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div class="rounded-lg border border-surface-border/70 bg-surface-dark/60 p-3">
            <p class="text-xs text-surface-muted">Total users</p>
            <p class="text-2xl font-semibold text-surface-light">{{ users.length }}</p>
          </div>
          <div class="rounded-lg border border-surface-border/70 bg-surface-dark/60 p-3">
            <p class="text-xs text-surface-muted">Superusers</p>
            <p class="text-2xl font-semibold text-surface-light">{{ superuserCount }}</p>
          </div>
          <div class="rounded-lg border border-surface-border/70 bg-surface-dark/60 p-3">
            <p class="text-xs text-surface-muted">Protected</p>
            <p class="text-2xl font-semibold text-surface-light">{{ protectedCount }}</p>
          </div>
          <div class="rounded-lg border border-surface-border/70 bg-surface-dark/60 p-3">
            <p class="text-xs text-surface-muted">Unverified</p>
            <p class="text-2xl font-semibold text-surface-light">{{ unverifiedCount }}</p>
          </div>
        </div>

        <div class="mt-5 grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto_auto] lg:items-end">
          <label class="text-xs font-medium text-surface-mid">
            Search users
            <input
              v-model="searchQuery"
              type="search"
              :class="[FIELD_INPUT_CLASS, 'mt-1']"
              placeholder="Search by name or email"
              aria-label="Search users by name or email"
            />
          </label>

          <label class="text-xs font-medium text-surface-mid">
            Role
            <select
              v-model="roleFilter"
              :class="[SELECT_CLASS_COMPACT, 'mt-1 block w-full lg:w-auto']"
              aria-label="Filter users by role"
            >
              <option value="all">All roles</option>
              <option value="superuser">Superusers</option>
              <option value="custom">Custom access</option>
            </select>
          </label>

          <label class="text-xs font-medium text-surface-mid">
            Status
            <select
              v-model="statusFilter"
              :class="[SELECT_CLASS_COMPACT, 'mt-1 block w-full lg:w-auto']"
              aria-label="Filter users by status"
            >
              <option value="all">All statuses</option>
              <option value="verified">Verified</option>
              <option value="unverified">Unverified</option>
              <option value="protected">Protected</option>
            </select>
          </label>
        </div>
      </BaseCard>
    </div>

    <div v-if="loading" class="space-y-4" aria-busy="true" aria-label="Loading users">
      <BaseCard v-for="index in 3" :key="index">
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
      </BaseCard>
    </div>

    <EmptyState v-else-if="users.length === 0">No users found.</EmptyState>

    <EmptyState v-else-if="filteredUsers.length === 0">
      No users match the current filters.
    </EmptyState>

    <div v-else class="space-y-5">
      <p class="text-xs text-surface-muted">
        Showing {{ filteredUsers.length }} of {{ users.length }} users
      </p>

      <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <button
          v-for="user in filteredUsers"
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
              <StatusBadge
                :label="roleLabel(user)"
                :class-name="
                  user.permissions.includes(SUPERUSER_PERMISSION)
                    ? 'bg-accent-violet/15 text-accent-violet border-accent-violet/30'
                    : 'bg-surface-dark text-surface-mid border-surface-border'
                "
              />
            </span>

            <span class="flex flex-wrap gap-2">
              <StatusBadge
                v-if="user.is_protected"
                label="protected"
                class-name="bg-accent-blue/15 text-accent-blue border-accent-blue/30"
              />
              <StatusBadge
                :label="user.is_verified ? 'verified' : 'unverified'"
                :class-name="
                  user.is_verified
                    ? 'bg-accent-golden/15 text-accent-golden border-accent-golden/30'
                    : 'bg-surface-dark text-surface-mid border-surface-border'
                "
              />
            </span>

            <span class="mt-auto flex items-center justify-between gap-3 text-xs text-surface-muted">
              <span>{{ permissionCount(user) }} permissions</span>
              <span>Joined {{ formatDate(user.created_at) }}</span>
            </span>
          </span>
        </button>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="selectedUser" class="fixed inset-0 z-50 flex justify-end">
        <Transition name="fade">
          <div
            v-if="selectedUser"
            class="absolute inset-0 bg-black/60 backdrop-blur-sm"
            @click="closeUserDrawer"
          />
        </Transition>

        <Transition name="drawer-slide" appear>
          <aside
            v-if="selectedUser"
            class="drawer-panel relative flex h-full w-full max-w-2xl flex-col border-l border-surface-border bg-surface-dark"
            aria-modal="true"
            role="dialog"
            :aria-label="`Edit permissions for ${selectedUser.display_name || selectedUser.email}`"
            @click.stop
          >
            <header
              class="flex shrink-0 items-start justify-between gap-3 border-b border-surface-border px-6 py-4"
            >
              <div class="min-w-0">
                <p class="text-xs font-medium uppercase tracking-wide text-surface-muted">
                  User permissions
                </p>
                <h2 class="mt-1 truncate text-lg font-bold text-surface-light">
                  {{ selectedUser.display_name || selectedUser.email }}
                </h2>
                <p class="mt-1 break-all text-xs text-surface-mid">{{ selectedUser.email }}</p>
              </div>
              <button
                type="button"
                class="rounded p-1 text-xl leading-none text-surface-mid hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
                aria-label="Close user permissions panel"
                @click="closeUserDrawer"
              >
                &times;
              </button>
            </header>

            <div class="flex-1 overflow-y-auto px-6 py-5">
              <div class="mb-5 space-y-3">
                <div class="flex flex-wrap gap-2">
                  <StatusBadge
                    :label="roleLabel(selectedUser)"
                    :class-name="
                      selectedUser.permissions.includes(SUPERUSER_PERMISSION)
                        ? 'bg-accent-violet/15 text-accent-violet border-accent-violet/30'
                        : 'bg-surface-dark text-surface-mid border-surface-border'
                    "
                  />
                  <StatusBadge
                    v-if="selectedUser.is_protected"
                    label="protected"
                    class-name="bg-accent-blue/15 text-accent-blue border-accent-blue/30"
                  />
                  <StatusBadge
                    :label="selectedUser.is_verified ? 'verified' : 'unverified'"
                    :class-name="
                      selectedUser.is_verified
                        ? 'bg-accent-golden/15 text-accent-golden border-accent-golden/30'
                        : 'bg-surface-dark text-surface-mid border-surface-border'
                    "
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
            </div>

            <footer
              class="shrink-0 border-t border-surface-border bg-surface-dark px-6 py-4"
            >
              <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <p class="text-xs text-surface-muted">
                  {{
                    hasDraftChanges(selectedUser)
                      ? "Unsaved permission changes"
                      : "Permissions are up to date"
                  }}
                </p>
                <div class="flex gap-2">
                  <BaseButton variant="ghost" @click="closeUserDrawer">Cancel</BaseButton>
                  <BaseButton
                    variant="primary"
                    :disabled="
                      savingId === selectedUser.id ||
                      selectedUser.is_protected ||
                      !hasDraftChanges(selectedUser)
                    "
                    @click="savePermissions(selectedUser)"
                  >
                    {{ savingId === selectedUser.id ? "Saving..." : "Save permissions" }}
                  </BaseButton>
                </div>
              </div>
            </footer>
          </aside>
        </Transition>
      </div>
    </Teleport>
  </AdminPageLayout>
</template>
